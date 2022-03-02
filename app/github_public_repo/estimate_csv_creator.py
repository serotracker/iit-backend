import logging
import os
import pandas as pd
from flask import current_app as app

from app.database_etl.airtable_records_handler import get_all_records, airtable_get_request

# Load env variables for Airtable request
AIRTABLE_API_KEY = app.config['AIRTABLE_API_KEY']
AIRTABLE_GITHUB_CSV_FIELDS_REQUEST_URL = app.config['AIRTABLE_GITHUB_CSV_FIELDS_REQUEST_URL']

# Get columns that should be pulled into CSV
headers = {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}
data = airtable_get_request(AIRTABLE_GITHUB_CSV_FIELDS_REQUEST_URL, headers)

# Get csv columns and create csv
try:
    # Extract fields
    records = data['records']
    fields = [x['fields']['Formal Column Label'] for x in records]
    snake_case_col_name = [x['fields']['Snake Case Column Label'] for x in records]
    logging.info("Successfully retrieved field names from Airtable")

    # Get estimates from Rapid Review: Estimates table for specified fields (Public CSV Included is an AT formula field)
    csv_records = get_all_records(fields, filters='&filterByFormula={Public CSV Included}=1')

    # Convert to df
    csv_records_df = pd.DataFrame.from_dict(csv_records)

    # For cols where values are in lists, extract from list
    multi_val_cols = ['isotypes', 'antibody_target', 'source_type', 'jbi_1', 'jbi_2', 'jbi_3', 'jbi_4', 'jbi_5',
                      'jbi_6', 'jbi_7', 'jbi_8', 'jbi_9', 'source_name', 'lead_institution', 'url', 'first_author',
                      'is_unity_aligned', 'publication_date', 'study_type', 'study_inclusion_criteria',
                      'study_exclusion_criteria']
    for col in multi_val_cols:
        csv_records_df[col] = csv_records_df[col].apply(lambda x: x[0] if x is not None else x)

    # Convert elements that are "Not reported" or "Not Reported" or "NR" to None
    csv_records_df.replace({'nr': None, 'NR': None, 'Not Reported': None, 'Not reported': None,
                            'Not available': None, 'NA': None, 'N/A': None}, inplace=True)

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
