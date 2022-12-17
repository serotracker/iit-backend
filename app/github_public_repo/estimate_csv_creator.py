import logging
import os
import pandas as pd
from flask import current_app as app

from app.database_etl.airtable_records_handler import get_all_records, airtable_get_request
from app.database_etl.airtable_records_handler.airtable_records_formatter import replace_null_fields


# Get use case of script from environment variable
csv_type = os.getenv('CSV_TYPE')

# Load env variables for Airtable request
AIRTABLE_API_KEY = app.config['AIRTABLE_API_KEY']

# Set URL and URL params based on script application
if csv_type == 'github':
    AIRTABLE_CSV_FIELDS_REQUEST_URL = app.config['GITHUB_CSV_FIELDS_REQUEST_URL']
    filter_by_formula = '&filterByFormula={GitHub CSV Included}=1'
else:
    AIRTABLE_CSV_FIELDS_REQUEST_URL = app.config['BIBLIO_CSV_FIELDS_REQUEST_URL']
    filter_by_formula = '&filterByFormula={Biblio CSV Included}=1'

# Get columns that should be pulled into CSV
headers = {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}
data = airtable_get_request(AIRTABLE_CSV_FIELDS_REQUEST_URL, headers)

# Get csv columns and create csv
try:
    # Extract fields based on the use case of the script (github csv or biblio csv)
    records = data['records']
    fields = [x['fields']['Formal Column Label'] for x in records]
    snake_case_col_name = [x['fields']['Snake Case Column Label'] for x in records]
    logging.info("Successfully retrieved field names from Airtable")

    # Get estimates from Rapid Review: Estimates table for specified fields
    csv_records = get_all_records(fields, filters=filter_by_formula)

    # Convert to df
    csv_records_df = pd.DataFrame.from_dict(csv_records)

    # List of columns that are lookup fields and therefore only have one element in the list
    single_element_list_cols = ['source_type', 'jbi_1', 'jbi_2', 'jbi_3', 'jbi_4',
                                'jbi_5', 'jbi_6', 'jbi_7', 'jbi_8a', 'jbi_8b', 'jbi_9', 'source_name', 'lead_institution', 'url',
                                'first_author', 'is_unity_aligned', 'publication_date', 'study_type',
                                'study_inclusion_criteria', 'study_exclusion_criteria', 'alpha_3_code',
                                'zotero_citation_key']
    csv_records_df_cols = csv_records_df.columns.values.tolist()
    for col in single_element_list_cols:
        # Check if the col exists in the dataframe because the cols pulled for github and biblio differ
        if col in csv_records_df_cols:
            csv_records_df[col] = csv_records_df[col].apply(lambda x: x[0] if x is not None else x)

    # Convert elements that are "Not reported" or "Not Reported" or "NR" to None
    csv_records_df.replace({'nr': None, 'NR': None, 'Not Reported': None, 'Not reported': None,
                            'Not available': None, 'NA': None, 'N/A': None}, inplace=True)

    # Antibody target and isotypes are multi select and will have ['Not reported'], ['NR'] - convert to None
    # Can also have a situation with ["Spike", "Not reported"] so need to check within list
    csv_records_df['antibody_target'] = csv_records_df['antibody_target'].apply(lambda x: replace_null_fields(x))
    csv_records_df['isotypes'] = csv_records_df['isotypes'].apply(lambda x: replace_null_fields(x))

    # If antibody_target and isotypes end up only having one element, remove from list
    for col in ['antibody_target', 'isotypes']:
        csv_records_df[col] = csv_records_df[col].apply(lambda x: x[0] if len(x) == 1 else x)

    # Reorder df columns based on airtable order
    csv_records_df = csv_records_df[snake_case_col_name]

    # Sort estimates by country, publication date, source name, study name, primary estimates first
    csv_records_df.sort_values(by=['country', 'publication_date', 'source_name',
                                   'study_name', 'dashboard_primary_estimate'], inplace=True)   
    # Save as csv
    abs_filepath_curr_dir = os.getcwd()
    proj_root_abs_path = abs_filepath_curr_dir.split("iit-backend")[0]
    csv_records_df.to_csv('serotracker_dataset.csv',
                          index=False)

except KeyError as e:
    logging.error(f"Failed to retrieve field names and load estimates. Error: {e}")
