import requests
import json
import os
import logging
from datetime import datetime
from uuid import uuid4

import pandas as pd
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)
AIRTABLE_REQUEST_PARAMS = {'filterByFormula': '{Visualize on SeroTracker?}=1'}
PATH = os.path.join(os.path.realpath(__file__), "../airtable_fields_config.json")


def _add_fields_to_url(url):
    # Add fields in config to api URL
    with open(PATH, 'r') as file:
        fields = json.load(file)
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
    with open(PATH, 'r') as file:
        fields = json.load(file)
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
        return request_info


def isotype_col(isotype_string, x):
    if x:
        return True if isotype_string in x else False
    return False


def create_airtable_source_df(original_data):
    # Length of records
    num_records = original_data.shape[0]

    # Create source id column
    source_id_col = [uuid4() for i in range(num_records)]
    original_data.insert(0, 'SOURCE_ID', source_id_col)

    # Create isotype boolean columns
    original_data['ISOTYPE_IGG'] = original_data['ISOTYPES'].apply(lambda x: isotype_col('IgG', x))
    original_data['ISOTYPE_IGM'] = original_data['ISOTYPES'].apply(lambda x: isotype_col('IgM', x))
    original_data['ISOTYPE_IGA'] = original_data['ISOTYPES'].apply(lambda x: isotype_col('IgA', x))
    original_data = original_data.drop(columns=['ISOTYPES'])

    # Create created at column
    original_data['CREATED_AT'] = datetime.now()

    # Convert the publication, sampling start date and sampling end date to datetime
    date_cols = ['PUBLICATION_DATE', 'SAMPLING_START_DATE', 'SAMPLING_END_DATE']
    for col in date_cols:
        original_data[col] =\
            original_data[col].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') if x is not None else x)
    return original_data


def create_multi_select_tables(original_data, cols):
    # Create dictionary to store multi select tables
    multi_select_tables_dict = {}
    for col in cols:
        id_col = '{}_ID'.format(col)
        name_col = '{}_NAME'.format(col)
        new_df_cols = [id_col, name_col]
        col_specific_df = pd.DataFrame(columns=new_df_cols)
        original_column = original_data[col].dropna()
        unique_nam_col = list({item for sublist in original_column for item in sublist})
        col_specific_df[name_col] = unique_nam_col
        col_specific_df[id_col] = [uuid4() for i in range(len(unique_nam_col))]
        multi_select_tables_dict[col] = col_specific_df
    return multi_select_tables_dict


def create_bridge_tables(original_data, multi_select_tables):
    multi_select_cols = multi_select_tables.keys()

    # Create bridge tables dict
    bridge_tables_dict = {}

    for col in multi_select_cols:
        id_col = '{}_ID'.format(col)
        name_col = '{}_NAME'.format(col)
        new_df_cols = ['ID', 'SOURCE_ID', id_col]
        bridge_table_df = pd.DataFrame(columns=new_df_cols)
        multi_select_table = multi_select_tables[col]
        for index, row in original_data.iterrows():
            col_options = row[col]
            source_id = row['SOURCE_ID']
            if col_options is not None:
                for option in col_options:
                    option_id = multi_select_table[multi_select_table[name_col] == option].iloc[0][id_col]
                    new_row = {'ID': uuid4(), 'SOURCE_ID': source_id, id_col: option_id}
                    bridge_table_df = bridge_table_df.append(new_row, ignore_index=True)
        bridge_tables_dict[col] = bridge_table_df
    return bridge_tables_dict


def main():
    json = get_all_records()
    data = pd.DataFrame(json)

    single_select_cols = ['SOURCE_NAME', 'PUBLICATION_DATE', 'FIRST_AUTHOR', 'URL', 'SOURCE_TYPE', 'SOURCE_PUBLISHER',
                          'SUMMARY', 'STUDY_TYPE', 'STUDY_STATUS', 'COUNTRY', 'LEAD_ORGANIZATION',
                          'OVERALL_RISK_OF_BIAS']

    multi_select_cols = ['CITY', 'STATE', 'AGE', 'POPULATION_GROUP', 'TEST_MANUFACTURER', 'APPROVING_REGULATOR',
                         'TEST_TYPE', 'SPECIMEN_TYPE']

    # Remove lists from single select columns
    for col in single_select_cols:
        data[col] = data[col].apply(lambda x: x[0] if x is not None else x)

    # Create airtable source df
    airtable_source = create_airtable_source_df(data)

    # Create dictionary to store multi select tables
    multi_select_tables_dict = create_multi_select_tables(data, multi_select_cols)

    # Create dictionary to store bridge tables
    bridge_tables_dict = create_bridge_tables(airtable_source, multi_select_tables_dict)

    # Drop columns not needed
    airtable_source = airtable_source.drop(columns=['CITY', 'STATE', 'AGE', 'POPULATION_GROUP',
                                                    'TEST_MANUFACTURER', 'APPROVING_REGULATOR', 'TEST_TYPE',
                                                    'SPECIMEN_TYPE'])
    print(airtable_source.columns)
    return


if __name__ == '__main__':
    # engine = create_engine('postgresql://{username}:{password}@localhost:5432/whiteclaw'.format(
    #     username=os.getenv('DATABASE_USERNAME'),
    #     password=os.getenv('DATABASE_PASSWORD')))
    main()
