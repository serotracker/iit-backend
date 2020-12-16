import requests
import json
import os
import logging
from datetime import datetime
from uuid import uuid4
from time import time
from marshmallow import ValidationError, INCLUDE
from dotenv import load_dotenv

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from app.serotracker_sqlalchemy import db_session, DashboardSource, ResearchSource, Country, City, State,\
    TestManufacturer, AntibodyTarget, CityBridge, StateBridge, TestManufacturerBridge, AntibodyTargetBridge,\
    DashboardSourceSchema, ResearchSourceSchema
from app.utils import airtable_fields_config, full_airtable_fields, send_api_error_email
from app.utils.send_error_email import send_schema_validation_error_email

load_dotenv()
logger = logging.getLogger(__name__)

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)

CURR_TIME = datetime.now()


def _add_fields_to_url(url):
    # Add fields in config to api URL
    fields = full_airtable_fields
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
    renamed_cols = full_airtable_fields
    total_records_df = total_records_df.rename(columns=renamed_cols)
    total_records_df = total_records_df.where(total_records_df.notna(), None)
    total_records_json = total_records_df.to_dict('records')
    return total_records_json


def _get_paginated_records(data, api_request_info):
    # Extract API request parameters
    url = api_request_info[0]
    headers = api_request_info[1]

    # Extract records from initial request response
    records = data['records']

    # Continue adding paginated records so long as there is an offset in the api response
    while 'offset' in list(data.keys()):
        r = requests.get(url, headers=headers, params={'offset': data['offset']})
        data = r.json()
        records += data['records']
    return records


def get_all_records():
    # Get airtable API URL and add fields to be scraped to URL in HTML format
    url = AIRTABLE_REQUEST_URL.format(AIRTABLE_BASE_ID)
    url = _add_fields_to_url(url)
    headers = {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}

    # Make request and retrieve records in json format
    r = requests.get(url, headers=headers)
    data = r.json()

    # Try to get records from data if the request was successful
    try:
        # If offset was included in data, retrieve additional paginated records
        if 'offset' in list(data.keys()):
            request_info = [url, headers]
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


def create_dashboard_source_df(original_data):
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
        bridge_tables_dict[f'{col}_bridge'] = bridge_table_df
    return bridge_tables_dict


def load_postgres_tables(tables_dict, engine):
    # Load dataframes into postgres tables
    for table_name, table_value in tables_dict.items():
        table_value.to_sql(table_name,
                           schema='public',
                           con=engine,
                           if_exists='append',
                           index=False)
    return


def drop_old_entries():
    all_tables = [DashboardSource, ResearchSource, City, State, TestManufacturer, AntibodyTarget, Country,
                  CityBridge, StateBridge, TestManufacturerBridge, AntibodyTargetBridge]
    with db_session() as session:
        for table in all_tables:
            # Drop record if it was not added during the current run
            session.query(table).filter(table.created_at != CURR_TIME).delete()
        session.commit()
    return


def validate_records(source, schema):
    source_dicts = source.to_dict(orient='records')
    acceptable_records = []
    unacceptable_records_map = {}  # Map each record to its error messages
    for record in source_dicts:
        try:
            schema.load(record, unknown=INCLUDE)
            acceptable_records.append(record)
        except ValidationError as err:
            try:
                # Pull source name as record title if record is from dashboard_source
                unacceptable_records_map[record['source_name']] = err.messages
            except KeyError:
                # Pull estimate name as record title if record is from research_source
                unacceptable_records_map[record['estimate_name']] = err.messages

    # Email unacceptable records and log to file here
    if unacceptable_records_map:
        send_schema_validation_error_email(unacceptable_records_map)

    if acceptable_records:
        return pd.DataFrame(acceptable_records)

    exit("EXITING – No acceptable records found.")


def get_coords(place_name, place_type):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{place_name}.json?" \
          f"access_token={os.getenv('MAPBOX_API_KEY')}"
    r = requests.get(url)
    data = r.json()
    coords = None
    if data and "features" in data and len(data['features']) > 0:
        coords = data['features'][0]['center']
        # Check if we have any results of the right place type
        # Otherwise fallback to the first result we get
        for feature in data['features']:
            if place_type in feature['place_type']:
                coords = feature['center']
                break
    return coords


def add_latlng_to_df(place_type, place_type_name, df):
    df['coords'] = df[place_type_name].map(lambda a: get_coords(a, place_type))
    df['longitude'] = df['coords'].map(lambda a: a[0] if isinstance(a, list) else None)
    df['latitude'] = df['coords'].map(lambda a: a[1] if isinstance(a, list) else None)
    df = df.drop(columns=['coords'])
    return df


def get_iso3(country_name):
    url = f"https://restcountries.eu/rest/v2/name/{country_name}"
    r = requests.get(url)
    data = r.json()
    iso3 = None
    try:
        idx = 0
        # try to find result with an exact name match
        # if one can't be found, default to index 0
        for i in range(len(data)):
            if data[i]["name"] == country_name:
                idx = i
                break
        iso3 = data[idx]["alpha3Code"]
    except:
        pass
    return iso3


def get_most_recent_publication_info(row):
    # Get index of most recent pub date if the pub date is not None
    try:
        pub_dates = row['publication_date']
        max_index = pub_dates.index(max(pub_dates))
        row['publication_date'] = row['publication_date'][max_index]

    # If pub date is None set to index to 0
    except AttributeError:
        max_index = 0

    # If source type exists, get element at that index
    if row['source_type']:
        row['source_type'] = row['source_type'][max_index]

    # Index whether org author exists and corresponding first author
    if row['organizational_author'] and row['first_author']:
        is_org_author = row['organizational_author'][max_index]
        row['organizational_author'] = is_org_author
        row['first_author'] = row['first_author'][max_index]

        # If it is not an organizational author, then get last name
        if not is_org_author and len(row['first_author']) > 0:
            row['first_author'] = row['first_author'].strip().split()[-1]
    return row


def apply_min_risk_of_bias(df):
    bias_hierarchy = ['Low', 'Moderate', 'High', 'Unclear']
    for name, subset in df.groupby('study_name'):
        if (subset['overall_risk_of_bias']).isnull().all():
            subset['overall_risk_of_bias'] = 'Unclear'
            continue
        for level in bias_hierarchy:
            if (subset['overall_risk_of_bias'] == level).any() or level == 'Unclear':
                subset['overall_risk_of_bias'] = level
                continue
    return df


def get_city(row):
    if row['city']:
        return row['city'].split(',')
    elif row['county']:
        return row['county'].split(',')
    else:
        return row['city']


def main():
    # Create engine to connect to whiteclaw database
    engine = create_engine('postgresql://{username}:{password}@{host_address}/whiteclaw'.format(
        username=os.getenv('DATABASE_USERNAME'),
        password=os.getenv('DATABASE_PASSWORD'),
        host_address=os.getenv('DATABASE_HOST_ADDRESS')))

    # Get all records with airtable API request and load into dataframe
    json = get_all_records()
    data = pd.DataFrame(json)

    # List of columns that are lookup fields and therefore only have one element in the list
    single_element_list_cols = ['included', 'source_name', 'url', 'source_publisher', 'summary',
                                'study_type', 'country', 'lead_organization', 'overall_risk_of_bias',
                                'age_variation', 'age_variation_measure', 'ind_eval_lab', 'ind_eval_link',
                                'ind_se', 'ind_se_n', 'ind_sp', 'ind_sp_n', 'jbi_1', 'jbi_2', 'jbi_3', 'jbi_4',
                                'jbi_5', 'jbi_6', 'jbi_7', 'jbi_8', 'jbi_9', 'measure_of_age', 'number_of_females',
                                'number_of_males', 'superceded', 'test_linked_uid', 'average_age',
                                'test_not_linked_reason']

    # Remove lists from single select columns
    for col in single_element_list_cols:
        data[col] = data[col].apply(lambda x: x[0] if x is not None else x)

    # Convert elements that are "Not reported" or "Not Reported" or "NR" to None
    data.replace({'NR': None, 'Not Reported': None, 'Not reported': None, 'Not available': None}, inplace=True)

    # Replace columns that should be floats with NaN from None
    data[['ind_sp_n', 'ind_se_n']] = data[['ind_sp_n', 'ind_se_n']].replace({None: np.nan})

    # Drop rows if columns are null: included?, serum pos prevalence, denominator, sampling end
    data.dropna(subset=['included', 'serum_pos_prevalence', 'denominator_value', 'sampling_end_date'],
                inplace=True)

    # Convert superceded to True/False values
    data['superceded'] = data['superceded'].apply(lambda x: True if x else False)

    # Get index of most recent publication date
    data = data.apply(lambda row: get_most_recent_publication_info(row), axis=1)

    # Convert state, city and test_manufacturer fields to lists
    data['state'] = data['state'].apply(lambda x: x.split(',') if x else x)
    data['test_manufacturer'] = data['test_manufacturer'].apply(lambda x: x.split(',') if x else x)
    data['city'] = data.apply(lambda row: get_city(row), axis=1)

    # Apply min risk of bias to all study estimates
    data = apply_min_risk_of_bias(data)

    # List of columns that are multi select (can have multiple values)
    multi_select_cols = ['city', 'state', 'test_manufacturer', 'antibody_target']

    # Create dashboard source df
    dashboard_source = create_dashboard_source_df(data)

    # Create country table df
    country_df = pd.DataFrame(columns=['country_name', 'country_id'])
    country_df['country_name'] = dashboard_source['country'].unique()
    country_df['country_id'] = [uuid4() for _ in country_df['country_name']]
    country_df['created_at'] = CURR_TIME
    country_df = add_latlng_to_df("country", "country_name", country_df)
    country_df['country_iso3'] = country_df["country_name"].map(lambda a: get_iso3(a))

    # temp code
    d = {}
    for index, row in country_df.iterrows():
        d[row['country_name']] = row['country_iso3']
    import json
    with open("country_iso3.json", 'w') as fout:
        json_dumps_str = json.dumps(d, indent=4)
        print(json_dumps_str, file=fout)

    # Add country_id's to dashboard_source df
    # country_dict maps country_name to country_id
    country_dict = {}
    for index, row in country_df.iterrows():
        country_dict[row['country_name']] = row['country_id']
    dashboard_source['country_id'] = dashboard_source['country'].map(lambda a: country_dict[a])

    # Create dictionary to store multi select tables
    multi_select_tables_dict = create_multi_select_tables(data, multi_select_cols)

    # Add lat/lng to cities and states
    state_df = add_latlng_to_df("region", "state_name", multi_select_tables_dict["state"])
    city_df = add_latlng_to_df("place", "city_name", multi_select_tables_dict["city"])
    multi_select_tables_dict["state"] = state_df
    multi_select_tables_dict["city"] = city_df

    # Create dictionary to store bridge tables
    bridge_tables_dict = create_bridge_tables(dashboard_source, multi_select_tables_dict)

    # Create research source table based on a subset of dashboard source df columns
    research_source_cols = list(airtable_fields_config['research'].values())
    research_source_cols.insert(0, 'source_id')
    research_source = dashboard_source[research_source_cols]

    # Drop antibody target col
    research_source = research_source.drop(columns=['antibody_target'])

    # Drop columns that are not needed not needed (don't drop source_id column though which is first element)
    dashboard_source_unused_cols = research_source_cols[1:] + ['organizational_author', 'city', 'county', 'state',
                                                               'test_manufacturer', 'country', 'antibody_target']
    dashboard_source = dashboard_source.drop(columns=dashboard_source_unused_cols)

    # Validate the dashboard source df
    dashboard_source = validate_records(dashboard_source, DashboardSourceSchema())
    research_source = validate_records(research_source, ResearchSourceSchema())

    # key = table name, value = table df
    tables_dict = {**multi_select_tables_dict, **bridge_tables_dict}
    tables_dict['dashboard_source'] = dashboard_source
    tables_dict['research_source'] = research_source
    tables_dict['country'] = country_df

    # Load dataframes into postgres tables
    load_postgres_tables(tables_dict, engine)

    # Delete old entries
    drop_old_entries()
    return


if __name__ == '__main__':
    beginning = time()
    main()
    diff = time() - beginning
    print(diff)
