import logging
from uuid import uuid4
from datetime import datetime

from app.utils.notifications_sender import send_slack_message
from app.utils import airtable_fields_config
from app.database_etl.location_utils import add_latlng_to_df, get_country_code
from .table_formatter import replace_null_string
from app.database_etl.owid_ingestion_handler import get_vaccinations_per_hundred, get_tests_per_hundred, get_deaths_per_hundred, get_cases_per_hundred, get_midpoint, get_whether_exact_match

import pandas as pd


def isotype_col(isotype_string, x):
    # Function for creating isotype boolean columns
    if x:
        return True if isotype_string in x else False
    return False


def create_dashboard_source_df(original_data, current_time):
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
    original_data['created_at'] = current_time

    # Convert the publication, sampling start date and sampling end date to datetime
    date_cols = ['publication_date', 'sampling_start_date', 'sampling_end_date']
    for col in date_cols:
        original_data[col] = \
            original_data[col].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') if x is not None else x)

    # Create midpoint date column
    original_data['sampling_midpoint_date'] = original_data.apply(
        lambda row: get_midpoint(row['sampling_start_date'], row['sampling_end_date']), axis=1)

    # Create total cases column
    original_data['cases_per_hundred'] = original_data.apply(lambda row: get_cases_per_hundred(row['country'], row['sampling_midpoint_date']),
                                                             axis=1)

    # Create total tests column
    original_data['tests_per_hundred'] = original_data.apply(lambda row: get_tests_per_hundred(row['country'], row['sampling_midpoint_date']),
                                                             axis=1)

    # Create total deaths column
    original_data['deaths_per_hundred'] = original_data.apply(
        lambda row: get_deaths_per_hundred(row['country'], row['sampling_midpoint_date']), axis=1)

    # Create vaccination count column
    original_data['vaccinations_per_hundred'] = original_data.apply(
        lambda row: get_vaccinations_per_hundred(row['country'], row['sampling_midpoint_date']), axis=1)

    # Create full vaccination count column
    original_data['full_vaccinations_per_hundred'] = original_data.apply(
        lambda row: get_vaccinations_per_hundred(row['country'], row['sampling_midpoint_date'], fully_vaccinated=True), axis=1)

    # Create flag denoting whether geographic mapping is 1:1
    original_data['geo_exact_match'] = original_data.apply(lambda row: get_whether_exact_match(row['country']), axis=1)

    original_data = original_data.drop(columns=['sampling_midpoint_date'])
    return original_data


def create_research_source_df(dashboard_source_df):
    # Create research source table based on a subset of dashboard source df columns
    # The airtable fields config columns are being pulled from airtable, the other 5 are manually created
    research_source_cols = list(airtable_fields_config['research'].values()) + ['gbd_region', 'gbd_subregion',
                                                                                'lmic_hic', 'genpop', 'sampling_type']
    research_source = dashboard_source_df[research_source_cols]

    # Add source id and created at columns from dashboard source df
    research_source.insert(0, 'source_id', dashboard_source_df['source_id'])
    research_source['created_at'] = dashboard_source_df['created_at']

    # Drop antibody target col
    research_source = research_source.drop(columns=['antibody_target'])

    # Remove any null string characters
    research_source = research_source.apply(lambda col: col.apply(lambda val: replace_null_string(val)))
    return research_source, research_source_cols


def create_multi_select_tables(original_data, current_time):
    # List of columns that are multi select (can have multiple values)
    multi_select_cols = ['city', 'state', 'test_manufacturer', 'antibody_target']

    # Create dictionary to store multi select tables
    multi_select_tables_dict = {}

    # Create country iso2 column, needed temporarily
    # to get lat/lngs for the state/city tables
    original_data['country_iso2'] = original_data['country'].map(lambda a: get_country_code(a, iso3=False))

    # Create one multi select table per multi select column
    for col in multi_select_cols:
        id_col = '{}_id'.format(col)
        name_col = '{}_name'.format(col)

        # Create dataframe for table with an id column, a name column, and a created_at column
        new_df_cols = [id_col, name_col, 'created_at']
        col_specific_df = pd.DataFrame(columns=new_df_cols)

        columns_to_grab = [col]
        # Need to subset country_iso2 col for state/city tables
        if col == "state" or col == "city":
            columns_to_grab.append('country_iso2')

        # create temporary dataframe to operate on
        temp_df = original_data[columns_to_grab]
        # explode the dataframe to make each multiselect element
        # its own row, then drop duplicates
        # note: drop_duplicates only drops entire duplicate rows
        # (so rows {city: c1, country_iso2: I1} and {city: c1, country_iso2: I2} would not be considered dupes)
        temp_df = temp_df.explode(col).drop_duplicates().dropna(subset=[col])

        # Create name all df columns and add as value to dictionary
        col_specific_df[name_col] = temp_df[col].to_list()
        # if city or state table, add country_iso2 column to df temporarily
        if col == "state" or col == "city":
            col_specific_df["country_iso2"] = temp_df["country_iso2"].to_list()
        col_specific_df[id_col] = [uuid4() for i in range(temp_df[col].size)]
        col_specific_df['created_at'] = current_time

        multi_select_tables_dict[col] = col_specific_df

    # Add lat/lng to cities and states
    # Get countries for each state
    multi_select_tables_dict["state"] = add_latlng_to_df("region", "state_name", multi_select_tables_dict["state"])
    multi_select_tables_dict["city"] = add_latlng_to_df("place", "city_name", multi_select_tables_dict["city"])

    # Delete country iso2 column, no longer needed
    # Note: only need this temporarily, so fine to drop
    multi_select_tables_dict["state"] = multi_select_tables_dict["state"].drop(columns=['country_iso2'])
    multi_select_tables_dict["city"] = multi_select_tables_dict["city"].drop(columns=['country_iso2'])
    original_data = original_data.drop(columns=['country_iso2'])

    return multi_select_tables_dict


def create_bridge_tables(original_data, multi_select_tables, current_time):
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
                    new_row = {'id': uuid4(), 'source_id': source_id, id_col: option_id, 'created_at': current_time}
                    bridge_table_df = bridge_table_df.append(new_row, ignore_index=True)
        bridge_tables_dict[f'{col}_bridge'] = bridge_table_df
    return bridge_tables_dict


def create_country_df(dashboard_source_df, current_time):
    country_df = pd.DataFrame(columns=['country_name', 'country_id', 'country_iso2'])
    country_df['country_name'] = dashboard_source_df['country'].unique()
    country_df['country_iso2'] = country_df['country_name'].map(lambda a: get_country_code(a, iso3=False))
    country_df['country_id'] = [uuid4() for _ in country_df['country_name']]
    country_df['created_at'] = current_time
    country_df = add_latlng_to_df("country", "country_name", country_df)
    country_df['country_iso3'] = country_df["country_name"].map(lambda a: get_country_code(a))

    # Note: only need this temporarily, so fine to drop
    country_df = country_df.drop(columns=['country_iso2'])

    # Send alert email if ISO3 codes not found
    null_iso3 = country_df[country_df['country_iso3'].isnull()]
    null_iso3_countries = list(null_iso3['country_name'])
    if len(null_iso3_countries) > 0:
        body = f"ISO3 codes were not found for the following countries: {null_iso3_countries}."
        logging.error(body)
        send_slack_message(body, channel='#dev-logging-etl')
    return country_df
