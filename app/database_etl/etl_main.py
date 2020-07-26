import requests
import json
import os
import logging
from datetime import datetime
from uuid import uuid4
from time import time

import pandas as pd
from sqlalchemy import create_engine
from app.sqlalchemy import db_session, AirtableSource, City, State, \
    Age, PopulationGroup, TestManufacturer, ApprovingRegulator, TestType, \
    SpecimenType, CityBridge, StateBridge, AgeBridge, PopulationGroupBridge, \
    TestManufacturerBridge, ApprovingRegulatorBridge, TestTypeBridge, SpecimenTypeBridge
from app.utils import airtable_fields_config, send_api_error_email

logger = logging.getLogger(__name__)

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)
AIRTABLE_REQUEST_PARAMS = {'filterByFormula': '{Visualize on SeroTracker?}=1'}

CURR_TIME = datetime.now()


def _add_fields_to_url(url):
    # Add fields in config to api URL
    fields = airtable_fields_config['dashboard']
    for key in fields:
        url += 'fields%5B%5D={}&'.format(key)
    url = url[:-1]
    return url


def _get_formatted_json_records(records):
    # Remove the created_at and id keys from each list item
    new_records = [record['fields'] for record in records]

    # Convert list of dictionaries to df
    total_records_df = pd.DataFrame(new_records)

    # Rename and reorder df columns according to formatted column names in config
    fields = airtable_fields_config['dashboard']
    renamed_cols = {key: fields[key] for key in fields}
    reordered_cols = [fields[key] for key in fields]
    total_records_df = total_records_df.rename(columns=renamed_cols)
    total_records_df = total_records_df[reordered_cols]
    total_records_df = total_records_df.where(total_records_df.notna(), None)
    total_records_json = total_records_df.to_dict('records')
    return total_records_json


def _get_paginated_records(data, api_request_info):
    # Extract API request parameters
    url = api_request_info[0]
    headers = api_request_info[1]
    parameters = api_request_info[2]

    # Extract records from initial request response
    records = data['records']

    # Continue adding paginated records so long as there is an offset in the api response
    while 'offset' in list(data.keys()):
        parameters['offset'] = data['offset']
        r = requests.get(url, headers=headers, params=parameters)
        data = r.json()
        records += data['records']
    return records


def get_all_records():
    # Get airtable API URL and add fields to be scraped to URL in HTML format
    url = AIRTABLE_REQUEST_URL.format(AIRTABLE_BASE_ID)
    url = _add_fields_to_url(url)
    headers = {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}
    params = AIRTABLE_REQUEST_PARAMS

    # Make request and retrieve records in json format
    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    # Try to get records from data if the request was successful
    try:
        # If offset was included in data, retrieve additional paginated records
        if 'offset' in list(data.keys()):
            parameters = params.copy()
            request_info = [url, headers, parameters]
            records = _get_paginated_records(data, request_info)
        else:
            records = data['records']
        formatted_records = _get_formatted_json_records(records)
        return formatted_records

    # If request was not successful, there will be no records field in response
    # Just return what is in cached layer and log an error
    except KeyError as e:
        body = "Results were not successfully retrieved from Airtable API." \
               "Please check connection parameters in config.py and fields in airtable_fields_config.json."
        logger.error(body)
        logger.error(f"Error Info: {e}")
        logger.error(f"API Response Info: {data}")

        request_info = {
            "url": url,
            "headers": json.dumps(headers)
        }

        send_api_error_email(body, data, error=e, request_info=request_info)
        return request_info


def isotype_col(isotype_string, x):
    # Function for creating isotype boolean columns
    if x:
        return True if isotype_string in x else False
    return False


def modify_date_col(x):
    # Convert to a datetime
    new_x = datetime.strptime(x, '%Y-%m-%d') if x is not None else x
    return new_x


def create_airtable_source_df(original_data):
    # Length of records
    num_records = original_data.shape[0]

    # Create source id column
    source_id_col = [uuid4() for i in range(num_records)]
    original_data.insert(0, 'source_id', source_id_col)

    # Create isotype boolean columns
    original_data['isotype_igg'] = original_data['isotypes'].apply(lambda x: isotype_col('IgG', x))
    original_data['isotype_igm'] = original_data['isotypes'].apply(lambda x: isotype_col('IgM', x))
    original_data['isotype_iga'] = original_data['isotypes'].apply(lambda x: isotype_col('IgA', x))
    original_data = original_data.drop(columns=['isotypes'])

    # Create created at column
    original_data['created_at'] = CURR_TIME

    # Convert the publication, sampling start date and sampling end date to datetime
    date_cols = ['publication_date', 'sampling_start_date', 'sampling_end_date']
    for col in date_cols:
        original_data[col] = \
            original_data[col].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') if x is not None else x)
    return original_data


def create_multi_select_tables(original_data, cols):
    # Create dictionary to store multi select tables
    multi_select_tables_dict = {}

    # Create one multi select table per multi select column
    for col in cols:
        id_col = '{}_id'.format(col)
        name_col = '{}_name'.format(col)

        # Create dataframe for table with an id column, a name column, and a created_at column
        new_df_cols = [id_col, name_col, 'created_at']
        col_specific_df = pd.DataFrame(columns=new_df_cols)
        original_column = original_data[col].dropna()

        # Get all unique values in the multi select column
        unique_nam_col = list({item for sublist in original_column for item in sublist})

        # Create name all df columns and add as value to dictionary
        col_specific_df[name_col] = unique_nam_col
        col_specific_df[id_col] = [uuid4() for i in range(len(unique_nam_col))]
        col_specific_df['created_at'] = CURR_TIME
        multi_select_tables_dict[col] = col_specific_df
    return multi_select_tables_dict


def create_bridge_tables(original_data, multi_select_tables):
    multi_select_cols = multi_select_tables.keys()

    # Create bridge tables dict
    bridge_tables_dict = {}

    # Create one bridge table per multi select column
    for col in multi_select_cols:
        id_col = '{}_id'.format(col)
        name_col = '{}_name'.format(col)

        # Create dataframe with id, source_id, multi select id and created at column
        new_df_cols = ['id', 'source_id', id_col, 'created_at']
        bridge_table_df = pd.DataFrame(columns=new_df_cols)
        multi_select_table = multi_select_tables[col]
        for index, row in original_data.iterrows():
            col_options = row[col]
            source_id = row['source_id']
            if col_options is not None:
                for option in col_options:
                    option_id = multi_select_table[multi_select_table[name_col] == option].iloc[0][id_col]
                    new_row = {'id': uuid4(), 'source_id': source_id, id_col: option_id, 'created_at': CURR_TIME}
                    bridge_table_df = bridge_table_df.append(new_row, ignore_index=True)
        bridge_tables_dict[col] = bridge_table_df
    return bridge_tables_dict


def load_postgres_tables(airtable_table, multi_select_tables_dict, bridge_tables_dict, engine):
    # Load dataframes into postgres tables
    airtable_table.to_sql('airtable_source',
                          schema='public',
                          con=engine,
                          if_exists='append',
                          index=False)

    for table_name, table_value in multi_select_tables_dict.items():
        table_value.to_sql(table_name,
                           schema='public',
                           con=engine,
                           if_exists='append',
                           index=False)

    for table_name, table_value in bridge_tables_dict.items():
        table_value.to_sql('{}_bridge'.format(table_name),
                           schema='public',
                           con=engine,
                           if_exists='append',
                           index=False)
    return


def drop_old_entries(engine):
    all_tables = [AirtableSource, City, State, Age, PopulationGroup,
                  TestManufacturer, ApprovingRegulator, TestType, SpecimenType,
                  CityBridge, StateBridge, AgeBridge, PopulationGroupBridge,
                  TestManufacturerBridge, ApprovingRegulatorBridge, TestTypeBridge, SpecimenTypeBridge]
    with db_session(engine) as session:
        for table in all_tables:
            # Drop record if it was not added during the current run
            query = session.query(table).filter(table.created_at != CURR_TIME).delete()
        session.commit()
    return


def main():
    # Create engine to connect to whiteclaw database
    engine = create_engine('postgresql://{username}:{password}@localhost/whiteclaw'.format(
        username=os.getenv('DATABASE_USERNAME'),
        password=os.getenv('DATABASE_PASSWORD')))

    # Get all records with airtable API request and load into dataframe
    json = get_all_records()
    data = pd.DataFrame(json)

    # List of columns that are single select (cannot have multiple values)
    single_select_cols = ['source_name', 'publication_date', 'first_author', 'url', 'source_type', 'source_publisher',
                          'summary', 'study_type', 'study_status', 'country', 'lead_organization',
                          'overall_risk_of_bias']

    # List of columns that are multi select (can have multiple values)
    multi_select_cols = ['city', 'state', 'age', 'population_group', 'test_manufacturer', 'approving_regulator',
                         'test_type', 'specimen_type']

    # Remove lists from single select columns
    for col in single_select_cols:
        data[col] = data[col].apply(lambda x: x[0] if x is not None else x)

    # Create airtable source df
    airtable_source = create_airtable_source_df(data)
    print(airtable_source.columns)
    print(airtable_source.iloc[0])
    # for i, r in airtable_source.iterrows():
    #     date = r['sampling_end_date']
    #     if date is not None and '2020' not in str(date):
    #         print(i)
    #         print(date)
    # exit()

    # Create dictionary to store multi select tables
    multi_select_tables_dict = create_multi_select_tables(data, multi_select_cols)

    # Create dictionary to store bridge tables
    bridge_tables_dict = create_bridge_tables(airtable_source, multi_select_tables_dict)

    # Drop columns that are not needed not needed
    airtable_source = airtable_source.drop(columns=['city', 'state', 'age', 'population_group',
                                                    'test_manufacturer', 'approving_regulator', 'test_type',
                                                    'specimen_type'])

    # Load dataframes into postgres tables
    load_postgres_tables(airtable_source, multi_select_tables_dict, bridge_tables_dict, engine)

    # Delete old entries
    drop_old_entries(engine)

    return


if __name__ == '__main__':
    beginning = time()
    main()
    diff = time() - beginning
    print(diff)
