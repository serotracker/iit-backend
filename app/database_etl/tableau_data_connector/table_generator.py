import os

import pandas as pd
from dotenv import load_dotenv

from app.utils import get_filtered_records
from app.database_etl.tableau_data_connector.google_services_manager import GoogleSheetsManager
from app.namespaces.data_provider.data_provider_service import jitter_pins

load_dotenv()


def upload_analyze_csv():
    # Get records
    records = get_filtered_records(research_fields=True, filters=None, columns=None, start_date=None,
                                   end_date=None, prioritize_estimates=False)
    records = jitter_pins(records)
    records_df = pd.DataFrame(records)
    s = records_df['sampling_start_date'][0]
    p = records_df['publication_date'][0]

    print(s, p)
    print(type(s), type(p))
    exit()

    # Turn lists into comma sep strings
    cols = ['city', 'state', 'test_manufacturer', 'antibody_target', 'isotypes_reported']
    for col in cols:
        records_df[col] = records_df[col].apply(lambda x: ",".join(x))

    # Clean df
    records_df['source_id'] = records_df['source_id'].apply(lambda x: str(x))
    records_df = records_df.fillna('')
    records_df = records_df.replace('[', '')
    records_df = records_df.replace(']', '')

    # Convert date fields to strings (otherwise get Timestamp is not JSON serializable error)
    # records_df[['publication_date', 'date_created', 'last_modified_time']] =\
    #     records_df[['publication_date', 'date_created', 'last_modified_time']].astype(str)

    # Upload df to google sheet
    g_client = GoogleSheetsManager()
    g_client.update_sheet(os.getenv('ANALYZE_SPREADSHEET_ID'), records_df)
    return

