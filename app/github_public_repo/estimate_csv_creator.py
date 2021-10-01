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
    fields = [x['fields']['Field Name'] for x in records]
    logging.info("Successfully retrieved field names from Airtable")

    # Get estimates from Rapid Review: Estimates table for specified fields
    csv_records = get_all_records(fields)

    # Convert to df, reorder cols alphabetically and as save as csv
    csv_records_df = pd.DataFrame.from_dict(csv_records)
    csv_records_df = csv_records_df.reindex(sorted(csv_records_df.columns), axis=1)
    abs_filepath_curr_dir = os.getcwd()
    proj_root_abs_path = abs_filepath_curr_dir.split("iit-backend")[0]
    csv_records_df.to_csv(f'{proj_root_abs_path}iit-backend/app/github_public_repo/serotracker_dataset.csv', index=False)

except KeyError as e:
    logging.error(f"Failed to retrieve field names and load estimates. Error: {e}")
