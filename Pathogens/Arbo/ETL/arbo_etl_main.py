import uuid
from datetime import datetime

import numpy as np
import random
from pyairtable import Table
import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import or_, table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from Pathogens.Arbo.ETL.constants import estimate_columns, single_select_lists
from Pathogens.Arbo.app.sqlalchemy import db_engine
from Pathogens.Arbo.app.sqlalchemy.sql_alchemy_base import Estimate, Antibody, AntibodyToEstimate
from Pathogens.Utility.location_utils.location_functions import get_city_lat_lng

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_ARBO_BASE_ID = os.getenv('AIRTABLE_ARBO_BASE_ID')
MINIMUM_SAMPLE_SIZE = 5
CURR_TIME = datetime.now()
MAXIMUM_PIN_JITTER_LATITUDE_OR_LONGITUDE = 0.1

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


def load_into_db(data, table_name, schema='arbo'):
    try:
        data.to_sql(table_name,
                    schema=schema,
                    con=db_engine,
                    if_exists='append',
                    index=False)
        print("[DB] " + table_name + " data uploaded to database")
        return True
    except (SQLAlchemyError, ValueError) as e:
        # Send slack error message
        body = f'[ERROR] Error occurred while loading {table_name} data into Postgres: {e}: '
        # print(body)
        return False


def load_antibody_data_into_db(data):
    try:
        for antibody_pair in data.itertuples():
            estimate_id = antibody_pair[1]
            antibodies = antibody_pair[2]
            with Session(db_engine) as session:
                for antibody_name in antibodies:
                    if antibody_name is not None:
                        antibody = session.query(Antibody).filter_by(antibody=antibody_name).first()
                        if antibody is None:
                            antibody = Antibody(id=uuid.uuid4(), antibody=antibody_name, created_at=CURR_TIME)
                            session.add(antibody)
                            session.commit()
                        antibody_estimate_relationship = AntibodyToEstimate(id=uuid.uuid4(), antibody_id=antibody.id,
                                                                            estimate_id=estimate_id, created_at=CURR_TIME)
                        session.add(antibody_estimate_relationship)
                session.commit()
        return True
    except SQLAlchemyError as e:
        print(f'[ERROR] Error occurred while loading antibody data into Postgres: {e} ')
        return False


def main():
    load_dotenv()

    fields_mapping = {'Source Sheet': 'source_sheet_id',
                      'Unique ID': 'estimate_id',
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
                      'Producer - Other': 'producer_other',
                      'WHO Region': 'who_region',
                      }

    source_sheet_fields_mapping = {
        'Source Title': 'source_sheet_name'
    }

    estimate_sheet_airtable = Table(os.getenv('AIRTABLE_API_KEY'), os.getenv('AIRTABLE_ARBO_BASE_ID'), 'Study/Estimate Sheet')
    source_sheet_airtable = Table(os.getenv('AIRTABLE_API_KEY'), os.getenv('AIRTABLE_ARBO_BASE_ID'), 'Source Sheet')

    #  TODO: Update all airtable requests to use pyairtable instead of hardcoded strings
    all_records = estimate_sheet_airtable.all(fields=fields_mapping.keys())
    records_df = pd.DataFrame.from_records([row["fields"] for row in all_records])
    records_df.rename(columns=fields_mapping, inplace=True)

    records_df['created_at'] = CURR_TIME

    # Convert elements that are "Not reported" or "Not Reported" or "NR" to None
    records_df.replace({'nr': None, 'NR': None, 'Not Reported': None, 'Not reported': None, 'Not available': None,
                        'NA': None, 'N/A': None, 'nan': None, np.nan: None}, inplace=True)

    

    records_df['id'] = [uuid.uuid4() for _ in range(len(records_df))]

    # flatten out single select lists
    for col in single_select_lists:
        records_df[col] = records_df[col].apply(lambda x: x[0] if x is not None else x)

    # Convert the publication, sampling start date and sampling end date to datetime
    date_cols = ['sample_start_date', 'sample_end_date']
    for col in date_cols:
        print("[STEP] Converting date string to datetime object for " + col)
        records_df[col] = records_df[col].apply(parse_date_cols)

    # print(records_df.dtypes)

    print("[STEP] Merging the estimate data with the source sheet data")
    source_sheet_records = source_sheet_airtable.all(fields=source_sheet_fields_mapping.keys())
    source_sheet_df = pd.DataFrame.from_records([row["fields"] for row in source_sheet_records])
    source_sheet_df['source_sheet_id'] = ([row['id'] for row in source_sheet_records])
    source_sheet_df.rename(columns=source_sheet_fields_mapping, inplace=True)
    records_df = pd.merge(records_df, source_sheet_df, on="source_sheet_id")

    print("[STEP] Removing fields that do not need to be saved in the database")
    records_df = records_df[records_df['include_in_etl'] == 1]

    print("[STEP] filtering out studies that don't meet the minimum sample size requirement (sample sizes must be >={})".format(MINIMUM_SAMPLE_SIZE))
    records_df.drop(records_df[records_df.sample_size < MINIMUM_SAMPLE_SIZE].index, inplace=True)

    print("[STEP] generating lat and lng values")

    lat_lng_report_file_path = "./lat_lng_generation_report.txt"
    with open(lat_lng_report_file_path, 'w') as lat_lng_report_file:
        records_df[['latitude', 'longitude']] = records_df.apply(lambda row:
            pd.Series(get_city_lat_lng(
                city_name=(row['city'] if pd.notnull(row['city']) else None),
                state_name=(row['state'] if pd.notnull(row['state']) else None),
                country_name=row['country'],
                lat_lng_report_file = lat_lng_report_file),
            dtype='object'), axis = 1
        )

    print('[INFO] Lat lng generation log report saved in your current working directory with the name "' + lat_lng_report_file_path + '". The old file was overwritten')

    print ("[STEP] adding random jitter to lat and lng values to distribute pins around.")
    for column in ['latitude', 'longitude']:
        records_df[column] = records_df[column].apply(lambda value: value + (random.uniform(-MAXIMUM_PIN_JITTER_LATITUDE_OR_LONGITUDE, MAXIMUM_PIN_JITTER_LATITUDE_OR_LONGITUDE)))

    dbs_loaded_successfully = True
    print("[STEP] loading estimate data into database")
    dbs_loaded_successfully = load_into_db(data=records_df[estimate_columns], table_name='estimate') and dbs_loaded_successfully

    # Replace antibody values with the keys to their the values in their tables
    # If value does not exist in the table then add it into the table and use the new id
    print("[STEP] loading antibody data into database")
    dbs_loaded_successfully = load_antibody_data_into_db(records_df[['id', 'antibody']]) and dbs_loaded_successfully

    if dbs_loaded_successfully:
        print("[STEP] deleting old data from database")
        with Session(db_engine) as session:
            session.query(AntibodyToEstimate).filter(AntibodyToEstimate.created_at != CURR_TIME).delete()
            session.query(Estimate).filter(Estimate.created_at != CURR_TIME).delete()
            session.commit()
    else:
        print("[ERROR] Issue above deleting new data from database")
        with Session(db_engine) as session:
            session.query(AntibodyToEstimate).filter(AntibodyToEstimate.created_at == CURR_TIME).delete()
            session.query(Estimate).filter(Estimate.created_at == CURR_TIME).delete()
            session.commit()


if __name__ == '__main__':
    print("Running Arbo ETL...")
    main()
