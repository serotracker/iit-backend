import os

import pandas as pd
from dotenv import load_dotenv

from app.utils import get_filtered_records
from app.database_etl.tableau_data_connector.google_services_manager import GoogleSheetsManager
from app.namespaces.data_provider.data_provider_service import jitter_pins

load_dotenv()


def upload_analyze_csv(canadian_data):
    # Get records
    estimates_subgroup = 'estimate_prioritization' if canadian_data else 'all'
    include_subgeography_estimates = True if canadian_data else False
    filters = {'country': ['Canada']} if canadian_data else None
    records = get_filtered_records(research_fields=True, filters=filters, columns=None, sampling_start_date=None,
                                   sampling_end_date=None, estimates_subgroup=estimates_subgroup,
                                   include_subgeography_estimates=include_subgeography_estimates)
    records = jitter_pins(records)
    records_df = pd.DataFrame(records)

    # Turn lists into comma sep strings
    cols = ['city', 'state', 'test_manufacturer', 'antibody_target', 'isotypes_reported']
    for col in cols:
        records_df[col] = records_df[col].apply(lambda x: ",".join(x))

    # Clean df
    records_df['source_id'] = records_df['source_id'].apply(lambda x: str(x))
    records_df = records_df.fillna('')
    records_df = records_df.replace('[', '')
    records_df = records_df.replace(']', '')

    # Upload df to google sheet
    sheet_name = 'Canadian data' if canadian_data else 'tableau_analyze_records'
    g_client = GoogleSheetsManager(sheet_name)
    g_client.update_sheet(spreadsheet_id=os.getenv('ANALYZE_SPREADSHEET_ID'),
                          df=records_df)
    return

