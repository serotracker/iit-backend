import requests
import os
import json
import logging
from datetime import datetime
from uuid import uuid4
from time import time
from marshmallow import ValidationError, INCLUDE
from dotenv import load_dotenv

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from app.serotracker_sqlalchemy import db_session, DashboardSource, ResearchSource, Country, City, State, \
    TestManufacturer, AntibodyTarget, CityBridge, StateBridge, TestManufacturerBridge, AntibodyTargetBridge, \
    DashboardSourceSchema, ResearchSourceSchema
from app.utils import airtable_fields_config, full_airtable_fields, send_api_error_email, send_email, get_filter_static_options
from app.utils.send_error_email import send_schema_validation_error_email


load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)

CURR_TIME = datetime.now()

table_names_dict = {
        "dashboard_source": DashboardSource,
        "research_source": ResearchSource,
        "city": City,
        "state": State,
        "test_manufacturer": TestManufacturer,
        "antibody_target": AntibodyTarget,
        "city_bridge": CityBridge,
        "state_bridge": StateBridge,
        "test_manufacturer_bridge": TestManufacturerBridge,
        "antibody_target_bridge": AntibodyTargetBridge,
        "country": Country
    }


# Note: this function takes in a relative path
def read_from_json(path_to_json):
    dirname = os.path.dirname(__file__)
    full_path = os.path.join(dirname, path_to_json)
    with open(full_path, 'r') as file:
        records = json.load(file)
    return records

ISO3_CODES = read_from_json('country_iso3.json')
ISO2_CODES = read_from_json('country_iso2.json')


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
        logging.error(body)
        logging.error(f"Error Info: {e}")
        logging.error(f"API Response Info: {data}")

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
        if table_name == 'research_source':
            table_value.loc[table_value['estimate_name'] == '0724_DeKalbFulton_CDCCOVID-19ResponseTeam_Female_PopAdj',
                            'jbi_2'] = 'somesuperlongstringthatwillcauseitalltofailhahahahhahahyessssss'
        try:
            table_value.to_sql(table_name,
                               schema='public',
                               con=engine,
                               if_exists='append',
                               index=False)
            drop_old_entries(table_name)
        except (SQLAlchemyError, ValueError) as e:
            # Send error email
            logging.error(e)
            # TODO: send slack message with error (include the table name that failed)

            # Delete  records in table that failed which contain current datetime (remove records from current ETL run)
            with db_session() as session:
                # Drop record if it was not added during the current run
                table = table_names_dict[table_name]
                session.query(table).filter(table.created_at == CURR_TIME).delete()
                session.commit()
    return


def drop_old_entries(table_name):
    table_names_dict = {
        "dashboard_source": DashboardSource,
        "research_source": ResearchSource,
        "city": City,
        "state": State,
        "test_manufacturer": TestManufacturer,
        "antibody_target": AntibodyTarget,
        "city_bridge": CityBridge,
        "state_bridge": StateBridge,
        "test_manufacturer_bridge": TestManufacturerBridge,
        "antibody_target_bridge": AntibodyTargetBridge,
        "country": Country
    }

    table = table_names_dict[table_name]
    with db_session() as session:
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


# Format of place: "{place_name}_{country_code}"
# Note country code is used as an optional argument to the mapbox api
# to improve search results, it might not exist
# If place_type is a "place" (meaning a city or town)
# place_name is only valid if it's in the format "city,state"
def get_coords(place, place_type):
    # If a city doesn't have a state
    # associated with it, we cannot
    # accurately find it's location
    if (not place) or (place_type == 'place' and "," not in place):
        return None

    # If place_name contains "_", then the string
    # after it should be an iso2 country code
    place_arr = place.split("_")

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{place_arr[0]}.json?" \
          f"access_token={os.getenv('MAPBOX_API_KEY')}&types={place_type}"

    if len(place_arr) > 1:
        url += f"&country={place_arr[1]}"

    r = requests.get(url)
    data = r.json()
    coords = None
    if data and "features" in data and len(data['features']) > 0:
        coords = data['features'][0]['center']
    return coords


def add_latlng_to_df(place_type, place_type_name, df):
    df['coords'] = df[place_type_name].map(lambda a: get_coords(a, place_type))
    df['longitude'] = df['coords'].map(lambda a: a[0] if isinstance(a, list) else None)
    df['latitude'] = df['coords'].map(lambda a: a[1] if isinstance(a, list) else None)
    df = df.drop(columns=['coords'])
    return df


# Get iso3 or iso2 code for a given country name
def get_country_code(country_name, iso3=True):
    code = None
    code_dict = ISO3_CODES if iso3 else ISO2_CODES
    if country_name in code_dict:
        code = code_dict[country_name]
    else:
        url = f"https://restcountries.eu/rest/v2/name/{country_name}"
        r = requests.get(url)
        data = r.json()
        try:
            idx = 0
            # try to find result with an exact name match
            # if one can't be found, default to index 0
            for i in range(len(data)):
                if data[i]["name"] == country_name:
                    idx = i
                    break
            code = data[idx]["alpha3Code"] if iso3 else data[idx]["alpha2Code"]
        except:
            pass
    return code


def add_mapped_variables(df):
    # Create mapped columns for gbd regions, subregion and lmic/hic countries
    gbd_mapping_country = pd.read_csv('../../shared_scripts/GBD_mapping/GBD_mapping_country.csv')
    gbd_region_col = []
    gbd_subregion_col = []
    for index, row in df.iterrows():
        country = row['country']
        gbd_row = gbd_mapping_country[gbd_mapping_country['Country'] == country]
        if gbd_row.shape[0] > 0:
            gbd_region_col.append(gbd_row.iloc[0]['GBD Region'])
            gbd_subregion_col.append(gbd_row.iloc[0]['GBD Subregion'])
        else:
            gbd_region_col.append(None)
            gbd_subregion_col.append(None)
    df['gbd_region'] = gbd_region_col
    df['gbd_subregion'] = gbd_subregion_col
    df['lmic_hic'] = df['gbd_region'].apply(
        lambda GBD_region: 'HIC' if GBD_region == 'High-income' else None if not GBD_region else 'LMIC')

    # Create general population vs special population field
    genpop_types = {'Household and community samples', 'Blood donors', 'Residual sera'}
    df['genpop'] = \
        df['population_group'].apply(lambda pop:
                                     'Study examining general population seroprevalence' if pop in genpop_types else
                                     'Study examining special population seroprevalence')

    # Create field for sampling type
    sampling_mapping = {
        'Unclear': 'Non-probability',
        'Self-referral/voluntary': 'Non-probability',
        'Convenience': 'Non-probability',
        'Entire sample': 'Probability',
        'Stratified random': 'Probability',
        'Simplified random': 'Probability',
        'Sequential': 'Non-probability',
        'Stratified non-random': 'Non-probability',
        'Simplified probability': 'Probability',
        'Randomized': 'Probability',
        'Stratified non-probability': 'Non-probability',
        'Self-referral': 'Non-probability',
        'Stratified probability': 'Probability',
        None: None
    }
    df['sampling_type'] = df['sampling_method'].map(sampling_mapping)
    return df


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


def apply_study_max_estimate_grade(df):
    grade_hierarchy = ['National', 'Regional', 'Local', 'Sublocal']
    for name, subset in df.groupby('study_name'):
        for level in grade_hierarchy:
            if (subset['estimate_grade'] == level).any():
                subset['estimate_grade'] = level
                continue
    return df


# Returns a list of 'city,state_countryCode' if we
# can associate a city with a state, else
# returns a list of cities
# This is necessary to properly geosearch cities
# as there can be multiple cities of the same name in a country
def get_city(row):
    if row['city']:
        cities = row['city'].split(',')
        # if only 1 state associated with the record
        # associate the city with the state
        # so that we can get a pin for it
        if row['state'] and len(row['state']) == 1:
            cities_return = []
            for city in cities:
                country_code = get_country_code(row['country'], iso3=False)
                if country_code:
                    cities_return.append(f"{city},{row['state'][0]}_{country_code}")
                else:
                    cities_return.append(f"{city},{row['state'][0]}")
            return cities_return
        return cities
    else:
        return row['city']


# Returns "state_countryCode"
# Needed becuase country code is used to limit mapbox API
# geosearch queries (improving query accuracy)
def add_country_code_to_state(row):
    if row['state']:
        states = []
        for state in row['state']:
            country_code = get_country_code(row['country'], iso3=False)
            if country_code:
                states.append(f"{state}_{country_code}")
            else:
                states.append(state)
        return states
    return None


# Send alert email if filter options have changed
def check_filter_options(dashboard_source):
    curr_filter_options = get_filter_static_options()
    to_ignore = set(["All", "Multiple groups", "Multiple populations", "Multiple Types", None])
    changed_filter_options = {}

    for filter_type in curr_filter_options:
        # Get new options for each filter type
        new_options = set(dashboard_source[filter_type].unique())
        # Remove options that are unused (e.g. "All", "Multiple groups", etc)
        new_options = set([s for s in new_options if s not in to_ignore])
        # Check to see if the new options are equal to the curr hardcoded options
        # Check to see if the new options are equal to the curr hardcoded options
        if new_options != set(curr_filter_options[filter_type]):
            changed_filter_options[filter_type] = new_options
            logging.info(new_options)
    if len(changed_filter_options.keys()) > 0:
        send_email(changed_filter_options, ["austin.atmaja@gmail.com"], "IIT BACKEND ALERT: Filter Options Have Changed")


# Replace None utf-8 encoded characters with blank spaces
def replace_null_string(x):
    if type(x) != str:
        return x
    encoded_val = x.encode('utf-8')
    if b'\x00' in encoded_val:
        encoded_val = encoded_val.replace(b'\x00', b'\x20')
        return encoded_val.decode('utf-8')
    return x


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

    # Replace columns that should be floats with NaN from None and rescale to percentage
    data[['ind_sp_n', 'ind_se_n']] = data[['ind_sp_n', 'ind_se_n']].replace({None: np.nan}) / 100

    # Drop rows if columns are null: included?, serum pos prevalence, denominator, sampling end
    data.dropna(subset=['included', 'serum_pos_prevalence', 'denominator_value', 'sampling_end_date'],
                inplace=True)

    # Convert superceded to True/False values
    data['superceded'] = data['superceded'].apply(lambda x: True if x else False)

    # Get index of most recent publication date
    data = data.apply(lambda row: get_most_recent_publication_info(row), axis=1)

    # Convert state, city and test_manufacturer fields to lists
    data['test_manufacturer'] = data['test_manufacturer'].apply(lambda x: x.split(',') if x else x)
    data['state'] = data['state'].apply(lambda x: x.split(',') if x else x)
    data['city'] = data.apply(lambda row: get_city(row), axis=1)
    data['state'] = data.apply(lambda row: add_country_code_to_state(row), axis=1)

    # Apply min risk of bias to all study estimates
    data = apply_min_risk_of_bias(data)

    # Apply study max estimate grade to all estimates in study
    data = apply_study_max_estimate_grade(data)

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
    country_df['country_iso3'] = country_df["country_name"].map(lambda a: get_country_code(a))

    # Send alert email if ISO3 codes not found
    null_iso3 = country_df[country_df['country_iso3'].isnull()]
    null_iso3_countries = list(null_iso3['country_name'])
    if len(null_iso3_countries) > 0:
        body = f"ISO3 codes were not found for the following countries: {null_iso3_countries}."
        logging.error(body)
        send_email(body, ["austin.atmaja@gmail.com", 'rahularoradfs@gmail.com',
                          'brettdziedzic@gmail.com'], "ALERT: ISO3 Codes Not Found")

    # Add country_id's to dashboard_source df
    # country_dict maps country_name to country_id
    country_dict = {}
    for index, row in country_df.iterrows():
        country_dict[row['country_name']] = row['country_id']
    dashboard_source['country_id'] = dashboard_source['country'].map(lambda a: country_dict[a])

    # Create dictionary to store multi select tables
    multi_select_tables_dict = create_multi_select_tables(data, multi_select_cols)

    # Add lat/lng to cities and states
    # Get countries for each state
    state_df = add_latlng_to_df("region", "state_name", multi_select_tables_dict["state"])
    city_df = add_latlng_to_df("place", "city_name", multi_select_tables_dict["city"])
    multi_select_tables_dict["state"] = state_df
    multi_select_tables_dict["city"] = city_df

    # Create dictionary to store bridge tables
    bridge_tables_dict = create_bridge_tables(dashboard_source, multi_select_tables_dict)

    # Add mapped variables to master dashboard source table
    dashboard_source = add_mapped_variables(dashboard_source)

    # Create research source table based on a subset of dashboard source df columns
    # The airtable fields config columns are being pulled from airtable, the other 5 are manually created
    research_source_cols = list(airtable_fields_config['research'].values()) + ['gbd_region', 'gbd_subregion',
                                                                                'lmic_hic', 'genpop', 'sampling_type']
    research_source = dashboard_source[research_source_cols]

    # Add source id and created at columns from dashboard source df
    research_source.insert(0, 'source_id', dashboard_source['source_id'])
    research_source['created_at'] = dashboard_source['created_at']

    # Drop antibody target col
    research_source = research_source.drop(columns=['antibody_target'])

    # Drop columns that are not needed in the dashboard source table
    dashboard_source_unused_cols = research_source_cols + ['organizational_author', 'city', 'county', 'state',
                                                           'test_manufacturer', 'country', 'antibody_target']
    dashboard_source = dashboard_source.drop(columns=dashboard_source_unused_cols)

    # Remove any null string characters from research source or dashboard source dfs
    research_source = research_source.apply(lambda col: col.apply(lambda val: replace_null_string(val)))
    dashboard_source = dashboard_source.apply(lambda col: col.apply(lambda val: replace_null_string(val)))

    # Adjust city and state table schema
    # Note this state_name field in the city table will never actually be used
    # but is nice to have for observability
    multi_select_tables_dict["city"]["state_name"] = multi_select_tables_dict["city"]["city_name"]\
        .map(lambda a: a.split("_")[0].split(",")[1] if "," in a else None)
    # remove state names from city_name field
    multi_select_tables_dict["city"]["city_name"] = multi_select_tables_dict["city"]["city_name"]\
        .map(lambda a: a.split(",")[0] if "," in a else a)
    multi_select_tables_dict["state"]["state_name"] = multi_select_tables_dict["state"]["state_name"]\
        .map(lambda a: a.split("_")[0])

    # Validate the dashboard source df
    dashboard_source = validate_records(dashboard_source, DashboardSourceSchema())
    research_source = validate_records(research_source, ResearchSourceSchema())

    # key = table name, value = table df
    tables_dict = {**multi_select_tables_dict, **bridge_tables_dict}
    tables_dict['dashboard_source'] = dashboard_source
    tables_dict['research_source'] = research_source
    tables_dict['country'] = country_df

    # Load dataframes into postgres tables
    # TODO: change how we are deleting records if ETL fails
    load_postgres_tables(tables_dict, engine)

    # Make sure that filter options are still valid
    check_filter_options(dashboard_source)

    return


if __name__ == '__main__':
    beginning = time()
    main()
    diff = time() - beginning
    print(diff)
