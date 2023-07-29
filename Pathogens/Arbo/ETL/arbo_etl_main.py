import uuid
from datetime import datetime

import numpy as np
from pyairtable import Table
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import or_, table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from Pathogens.Arbo.ETL.constants import estimate_columns, single_select_lists
from Pathogens.Arbo.app.sqlalchemy import db_engine
from Pathogens.Arbo.app.sqlalchemy.sql_alchemy_base import Estimate
from Pathogens.Utility.location_utils.location_functions import get_lng_lat

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

    fields_mapping = {'Source Sheet': 'source_sheet_id',
                      'Inclusion Criteria': 'inclusion_criteria',
                      'Sample Start Date': 'sample_start_date',
                      'Sample End Date': 'sample_end_date',
                      'Sex': 'sex',
                      'Pathogen': 'pathogen',
                      'Antibody': 'antibody',
                      'Antigen': 'antigen',
                      'Assay': 'assay',
                      'Assay - Other': 'assay_other',
                      'Sample Size': 'sample_size',
                      'Sample Numerator': 'sample_numerator',
                      'Sample Frame': 'sample_frame',
                      'Seroprevalence': 'seroprevalence',
                      'Country': 'country',
                      'State': 'state',
                      'City': 'city',
                      'URL': 'url',
                      'Age group': 'age_group',
                      'Age Minimum': 'age_minimum',
                      'Age Maximum': 'age_maximum',
                      'ETL Included': 'include_in_etl',
                      'Producer': 'producer',
                      'Producer - Other': 'producer_other'
                      }

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
                                                             pd.Series(get_lng_lat(
                                                                 ','.join(filter(None, [row['city'], row['state']])),
                                                                 'place'), dtype='object')
                                                             if pd.notnull(row['city']) and pd.notnull(row['state'])
                                                             else (pd.Series(
                                                                 get_lng_lat(row['state'], 'region'),
                                                                 dtype='object') if pd.notnull(
                                                                 row['state'])
                                                                   else pd.Series(
                                                                 get_lng_lat(row['country'], 'country'),
                                                                 dtype='object')), axis=1)

    db_loaded_successfully = False

    try:
        records_df[estimate_columns].to_sql("estimate",
                                            schema='arbo',
                                            con=db_engine,
                                            if_exists='append',
                                            index=False)
        print("Completed running... Verify in database...")
        db_loaded_successfully = True
    except (SQLAlchemyError, ValueError) as e:
        # Send slack error message
        body = f'Error occurred while loading tables into Postgres: {e}'
        print(body)

    if db_loaded_successfully:
        with Session(db_engine) as session:
            session.query(Estimate).filter(or_(table.created_at != CURR_TIME, table.created_at.is_(None))).delete()


if __name__ == '__main__':
    print("Running Arbo ETL...")
    main()
