import uuid
from datetime import datetime

import numpy as np
from pyairtable import Table
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from Pathogens.Utility.location_utils.location_functions import get_LngLat

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_ARBO_BASE_ID = os.getenv('AIRTABLE_ARBO_BASE_ID')
CURR_TIME = datetime.now()

def parse_date_cols(x):
    if x:
        new_date = datetime.strptime(x, '%Y-%m-%d')
        return new_date
    return None


def flatten_single_select_lists(x):
    if isinstance(x, list) and len(x) == 1:
        return x[0]
    else:
        return x


def main():
    load_dotenv()

    engine = create_engine(os.environ.get('DATABASE_URL'))

    fields_mapping = {'Source Sheet': 'source_sheet',
                      'Inclusion Criteria': 'inclusion_criteria',
                      'Sample Start Date': 'sample_start_date',
                      'Sample End Date': 'sample_end_date',
                      'Sex': 'sex',
                      'Pathogen': 'pathogen',
                      'Antibody': 'antibody',
                      'Antigen': 'antigen',
                      'Assay': 'assay',
                      'Sample Size': 'sample_size',
                      'Sample Numerator': 'sample_numerator',
                      'Sample Frame': 'sample_frame',
                      'Seroprevalence': 'seroprevalence',
                      'Country': 'country',
                      'State': 'state',
                      'City': 'city',
                      'URL': 'url',
                      'Age group': 'age_group',
                      'ETL Included': 'include_in_etl'}



    # Unused at the moment. Keeping here in case needed
    required_fields = ['sample_start_date', 'sex', 'assay', 'sample_size', 'age_group',
                       'sample_frame', 'seroprevalence', 'url', 'antibody', 'country', 'pathogen', 'source_sheet']

    single_select_lists = ['source_sheet', 'antibody', 'url']

    estimate_table = Table(os.getenv('AIRTABLE_API_KEY'), os.getenv('AIRTABLE_ARBO_BASE_ID'), 'Study/Estimate Sheet')

    #  TODO: Update all airtable requests to use pyairtable instead of hardcoded strings
    all_records = estimate_table.all(fields=fields_mapping.keys())
    records_df = pd.DataFrame.from_records([row["fields"] for row in all_records])
    records_df.rename(columns=fields_mapping, inplace=True)

    records_df['created_at'] = CURR_TIME

    # Convert elements that are "Not reported" or "Not Reported" or "NR" to None
    records_df.replace({'nr': None, 'NR': None, 'Not Reported': None, 'Not reported': None, 'Not available': None,
                        'NA': None, 'N/A': None, 'nan': None, np.nan: None}, inplace=True)

    # Drop records when include_in_etl is not 1
    records_df = records_df[records_df['include_in_etl'] == 1]

    records_df['id'] = [uuid.uuid4() for _ in range(len(records_df))]

    for col in single_select_lists:
        records_df[col] = records_df[col].apply(lambda x: x[0] if x is not None else x)

    print(records_df.columns)
    print(records_df.head(20).to_string())

    # Convert the publication, sampling start date and sampling end date to datetime
    date_cols = ['sample_start_date', 'sample_end_date']
    for col in date_cols:
        print("Converting date string to datetime object for " + col)
        records_df[col] = records_df[col].apply(parse_date_cols)

    print(records_df.dtypes)

    # calculate the lat and lng values for each of the rows.
    records_df[['latitude', 'longitude']] = records_df.apply(lambda row:
                                                             pd.Series(get_LngLat(
                                                                 ','.join(filter(None, [row['city'], row['state']])),
                                                                 'place'), dtype='object')
                                                             if pd.notnull(row['city']) and pd.notnull(row['state'])
                                                             else (pd.Series(
                                                                 get_LngLat(row['state'], 'region'), dtype='object') if pd.notnull(
                                                                 row['state'])
                                                                   else pd.Series(
                                                                 get_LngLat(row['country'], 'country'), dtype='object')), axis=1)

    # TODO: Add 'country', 'state', 'city' once the alembic stuff is fixed
    estimate_columns = ['id', 'inclusion_criteria', 'sample_start_date', 'sample_end_date', 'sex', 'assay',
                        'sample_size', 'sample_numerator', 'seroprevalence', 'url', 'longitude', 'latitude']

    try:
        records_df[estimate_columns].to_sql("estimates",
                                            schema='arbo',
                                            con=engine,
                                            if_exists='replace',
                                            index=False)
        print("Completed running... Verify in database...")
    except (SQLAlchemyError, ValueError) as e:
        # Send slack error message
        body = f'Error occurred while loading tables into Postgres: {e}'
        print(body)


if __name__ == '__main__':
    print("Running Arbo ETL...")
    main()
