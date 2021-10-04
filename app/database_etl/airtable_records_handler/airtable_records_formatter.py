import os
import json
from typing import Dict

import numpy as np
import pandas as pd
from pyairtable import Table

from ..location_utils import get_city
from app.utils import full_airtable_fields


# Converts a dict with single to double quotes: dict needs to be in this format for Airtable API to work
class doubleQuoteDict(dict):
    def __str__(self):
        return json.dumps(self)

    def __repr__(self):
        return json.dumps(self)


def get_most_recent_publication_info(row: Dict) -> Dict:
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
        # We should take either the max_index based on the latest pub date,
        # or the last element of source type if the max index doesn't exist
        i = min(max_index, len(row['source_type']) - 1)
        row['source_type'] = row['source_type'][i]

    # If zotero citation key exists, get element at that index
    if row['zotero_citation_key']:
        # We should take either the max_index based on the latest pub date,
        # or the last element of source type if the max index doesn't exist
        i = min(max_index, len(row['zotero_citation_key']) - 1)
        row['zotero_citation_key'] = row['zotero_citation_key'][i]

    # Index whether org author exists and corresponding first author
    if row['organizational_author'] and row['first_author']:
        # We should take either the max_index based on the latest pub date,
        # or the last element of org author if the max index doesn't exist
        i = min(max_index, len(row['organizational_author']) - 1)
        is_org_author = row['organizational_author'][i]
        row['organizational_author'] = is_org_author

        # We should take either the max_index based on the latest pub date,
        # or the last element of first author if the max index doesn't exist
        i = min(max_index, len(row['first_author']) - 1)
        row['first_author'] = row['first_author'][i]

        # If it is not an organizational author, then get last name
        if not is_org_author and len(row['first_author']) > 0:
            row['first_author'] = row['first_author'].strip().split()[-1]

    return row


def standardize_airtable_data(df: pd.DataFrame) -> pd.DataFrame:
    # List of columns that are lookup fields and therefore only have one element in the list
    single_element_list_cols = ['included', 'source_name', 'url', 'source_publisher', 'summary',
                                'study_type', 'lead_organization', 'age_variation', 'age_variation_measure',
                                'ind_eval_lab', 'ind_eval_link', 'ind_se', 'ind_se_n', 'ind_sp', 'ind_sp_n',
                                'jbi_1', 'jbi_2', 'jbi_3', 'jbi_4', 'jbi_5', 'jbi_6', 'jbi_7', 'jbi_8', 'jbi_9',
                                'measure_of_age', 'number_of_females', 'number_of_males', 'test_linked_uid',
                                'average_age',
                                'test_not_linked_reason', 'include_in_srma', 'is_unity_aligned']

    # Remove lists from single select columns
    for col in single_element_list_cols:
        df[col] = df[col].apply(lambda x: x[0] if x is not None else x)

    # Convert elements that are "Not reported" or "Not Reported" or "NR" to None
    df.replace({'nr': None, 'NR': None, 'Not Reported': None, 'Not reported': None,
                'Not available': None, 'NA': None}, inplace=True)

    # Replace columns that should be floats with NaN from None
    # IMPORTANT: ind_sp and ind_se are percentages but stored as ints in airtable so must convert to decimal!
    df[['ind_sp', 'ind_se']] = df[['ind_sp', 'ind_se']].replace({None: np.nan}) / 100

    # Get index of most recent publication date
    df = df.apply(lambda row: get_most_recent_publication_info(row), axis=1)

    # Convert unity alignment variable to a bool
    df['is_unity_aligned'] = df['is_unity_aligned'].apply(lambda x: True if x == 'Unity-Aligned' else False)

    # df state, city and test_manufacturer fields to lists
    df['test_manufacturer'] = df['test_manufacturer'].apply(lambda x: x.split(',') if x else x)
    df['state'] = df['state'].apply(lambda x: x.split(',') if x else x)
    df['city'] = df.apply(lambda row: get_city(row), axis=1)
    return df


def apply_min_risk_of_bias(df: pd.DataFrame) -> pd.DataFrame:
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


def apply_study_max_estimate_grade(df: pd.DataFrame) -> pd.DataFrame:
    grade_hierarchy = ['National', 'Regional', 'Local', 'Sublocal']
    for name, subset in df.groupby('study_name'):
        for level in grade_hierarchy:
            if (subset['estimate_grade'] == level).any():
                subset['estimate_grade'] = level
                continue
    return df


def batch_update_airtable_records(records_to_update, field_names):
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

    # Create table object
    table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, 'Rapid Review: Estimates')

    # Cycle through all the records to update
    for i, row in records_to_update.iterrows():
        # For each record, create a dict where the key is the field name and the value is the new field value
        # airtable_fields_config converts a readable english column name into a codified column name
        # e.g. x = 'Adjusted sensitivity', airtable_fields_config[x] = 'adj_sensitivity', row['adj_sensitivity'] = 0.9
        # If the value is NaN, convert to None because NaN throws error with Airtable API
        fields = {x: row[full_airtable_fields[x]] if not pd.isna(row[full_airtable_fields[x]]) else None for x in field_names}
        fields = doubleQuoteDict(fields)
        id = row['airtable_record_id']
        table.update(id, fields)
    return
