import os

import pandas as pd


# Replace None utf-8 encoded characters with blank spaces
def replace_null_string(x):
    if type(x) != str:
        return x
    encoded_val = x.encode('utf-8')
    if b'\x00' in encoded_val:
        encoded_val = encoded_val.replace(b'\x00', b'\x20')
        return encoded_val.decode('utf-8')
    return x


def add_mapped_variables(df):
    # Create mapped columns for gbd regions, subregion and lmic/hic countries
    path = os.path.dirname(os.path.dirname(os.getcwd())) + '/shared_scripts/GBD_mapping/GBD_mapping_country.csv'
    gbd_mapping_country = pd.read_csv(path)
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


def format_dashboard_source(dashboard_source_df, research_cols):
    # Drop columns that are not needed in the dashboard source table
    dashboard_source_unused_cols = research_cols + ['organizational_author', 'city', 'county', 'state',
                                                    'test_manufacturer', 'country', 'antibody_target']
    dashboard_source = dashboard_source_df.drop(columns=dashboard_source_unused_cols)

    # Remove any null string characters from research source or dashboard source dfs
    dashboard_source = dashboard_source.apply(lambda col: col.apply(lambda val: replace_null_string(val)))
    return dashboard_source

