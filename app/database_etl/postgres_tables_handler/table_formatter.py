import os
import logging

import pandas as pd

from app.utils.notifications_sender import send_slack_message


# Replace None utf-8 encoded characters with blank spaces
def replace_null_string(x):
    if type(x) != str:
        return x
    encoded_val = x.encode('utf-8')
    if b'\x00' in encoded_val:
        encoded_val = encoded_val.replace(b'\x00', b'\x20')
        return encoded_val.decode('utf-8')
    return x


def get_WHO_mapped_variables(country: str, gbd_mapping_df: pd.DataFrame):
    # Get row in GBD mapping DF that corresponds to the input country
    gbd_row = gbd_mapping_df[gbd_mapping_df['Country'] == country]
    if not gbd_row.empty:
        return gbd_row.iloc[0]['GBD Region'], gbd_row.iloc[0]['GBD Subregion'], gbd_row.iloc[0]['WHO region']
    else:
        return None, None, None


def add_mapped_variables(df):
    # Create mapped columns for gbd regions, subregion and lmic/hic countries
    path = os.path.dirname(os.path.abspath(__file__)) + '/GBD_mapping_country.csv'
    gbd_mapping_country = pd.read_csv(path)
    df['gbd_region'], df['gbd_subregion'], df['who_region'] = \
        zip(*df['country'].map(lambda x: get_WHO_mapped_variables(x, gbd_mapping_country)))

    # Add logging for countries without available GBD mappings
    # Get set of all countries that exist in df but not in gbd_mapping_country
    # See https://realpython.com/python-sets/#operators-vs-methods
    countries_with_no_mapping = set(df['country']) - set(gbd_mapping_country['Country'])
    if len(countries_with_no_mapping) > 0:
        body = 'No GBD region or subregion found for the following countries: '
        for country in countries_with_no_mapping:
            body += f'{country}, '
        logging.warning(body)
        send_slack_message(body, channel='#dev-logging-etl')

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


def format_dashboard_source(dashboard_source_df, research_cols):
    # Drop columns that are not needed in the dashboard source table
    dashboard_source_unused_cols = research_cols + ['organizational_author', 'city', 'county', 'state',
                                                    'test_manufacturer', 'country', 'antibody_target']
    dashboard_source = dashboard_source_df.drop(columns=dashboard_source_unused_cols)

    # Remove any null string characters from research source or dashboard source dfs
    dashboard_source = dashboard_source.apply(lambda col: col.apply(lambda val: replace_null_string(val)))
    return dashboard_source
