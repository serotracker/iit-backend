import multiprocessing

import numpy as np
from typing import Dict
import pandas as pd

from ..location_utils import get_city
from app.serotracker_sqlalchemy import db_session, ResearchSource, DashboardSource
from app.database_etl.test_adjustment_handler import TestAdjHandler


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
                                'study_type', 'country', 'lead_organization', 'overall_risk_of_bias',
                                'age_variation', 'age_variation_measure', 'ind_eval_lab', 'ind_eval_link',
                                'ind_se', 'ind_se_n', 'ind_sp', 'ind_sp_n', 'jbi_1', 'jbi_2', 'jbi_3', 'jbi_4',
                                'jbi_5', 'jbi_6', 'jbi_7', 'jbi_8', 'jbi_9', 'measure_of_age', 'number_of_females',
                                'number_of_males', 'test_linked_uid', 'average_age',
                                'test_not_linked_reason', 'include_in_srma']

    # Remove lists from single select columns
    for col in single_element_list_cols:
        df[col] = df[col].apply(lambda x: x[0] if x is not None else x)

    # Convert elements that are "Not reported" or "Not Reported" or "NR" to None
    df.replace({'nr': None, 'NR': None, 'Not Reported': None, 'Not reported': None, 'Not available': None},
               inplace=True)

    # Replace columns that should be floats with NaN from None and rescale to percentage
    df[['ind_sp', 'ind_se']] = df[['ind_sp', 'ind_se']].replace({None: np.nan}) / 100

    # Get index of most recent publication date
    df = df.apply(lambda row: get_most_recent_publication_info(row), axis=1)

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


def add_test_adjustments(df: pd.DataFrame) -> pd.DataFrame:
    # Query record ids in our database
    with db_session() as session:
        total_db_records = session.query(DashboardSource.serum_pos_prevalence,
                                         DashboardSource.test_adj,
                                         DashboardSource.sensitivity,
                                         DashboardSource.specificity,
                                         DashboardSource.test_type,
                                         DashboardSource.denominator_value,
                                         ResearchSource.ind_se,
                                         ResearchSource.ind_sp,
                                         ResearchSource.ind_se_n,
                                         ResearchSource.ind_sp_n,
                                         ResearchSource.se_n,
                                         ResearchSource.sp_n,
                                         ResearchSource.test_validation,
                                         ResearchSource.airtable_record_id) \
            .join(ResearchSource, ResearchSource.source_id == DashboardSource.source_id, isouter=True).all()
        total_db_records = [q._asdict() for q in total_db_records]
        total_db_records = pd.DataFrame(data=total_db_records)

    # Concat old and new records and fillna with 0 (NaN and None become 0 so it is standardized)
    diff = pd.concat([df, total_db_records])
    diff.fillna(0, inplace=True)

    # Convert numeric cols to float (some of these come out of airtable as strings so need to standardize types)
    float_cols = ['ind_se', 'ind_sp', 'ind_se_n', 'ind_sp_n', 'se_n', 'sp_n', 'sensitivity', 'specificity',
                  'denominator_value', 'serum_pos_prevalence']
    diff[float_cols] = diff[float_cols].astype(float)

    # Round float columns to a consistent number of decimal places to ensure consistent float comparisons
    diff[float_cols] = diff[float_cols].round(5)

    # Drop duplicates based on these cols
    duplicate_cols = ['airtable_record_id', 'test_adj', 'ind_se', 'ind_sp', 'ind_se_n', 'ind_sp_n',
                      'se_n', 'sp_n', 'sensitivity', 'specificity', 'test_validation', 'test_type', 'denominator_value',
                      'serum_pos_prevalence']
    diff = diff.drop_duplicates(subset=duplicate_cols, keep=False)

    # Get all unique airtable_record_ids that are new/have been modified
    new_airtable_record_ids = diff['airtable_record_id'].unique()

    # Add all unique airtable_record_ids for which test adjustment was unsuccessful 
    # TODO: MUST BE COMMENTED OUT IN PROD
    unadjusted_airtable_record_ids = total_db_records[total_db_records['adj_prevalence'].isna()]['airtable_record_id'].unique()
    new_airtable_record_ids = set.union(set(new_airtable_record_ids.unique()), 
                                        set(unadjusted_airtable_record_ids.unique()))

    # Get all rows from airtable data that need to be test adjusted, and ones that don't
    old_airtable_test_adj_records = \
        df[~df['airtable_record_id'].isin(new_airtable_record_ids)].reset_index(
            drop=True)
    new_airtable_test_adj_records = \
        df[df['airtable_record_id'].isin(new_airtable_record_ids)].reset_index(
            drop=True)
    # Add temporary boolean column if record will be test adjusted or not
    old_airtable_test_adj_records['test_adjusted_record'] = False
    new_airtable_test_adj_records['test_adjusted_record'] = True

    # Only proceed with test adjustment if there are new unadjusted records
    if not new_airtable_test_adj_records.empty:
        # Apply test adjustment to the new_test_adj_records and add 6 new columns
        multiprocessing.set_start_method("fork")
        test_adj_handler = TestAdjHandler()
        new_airtable_test_adj_records['adj_prevalence'], \
        new_airtable_test_adj_records['adj_sensitivity'], \
        new_airtable_test_adj_records['adj_specificity'], \
        new_airtable_test_adj_records['ind_eval_type'], \
        new_airtable_test_adj_records['adj_prev_ci_lower'], \
        new_airtable_test_adj_records['adj_prev_ci_upper'] = \
            zip(*new_airtable_test_adj_records.apply(lambda x: test_adj_handler.get_adjusted_estimate(x), axis=1))

    # If there are no old test adjusted records, just return the new ones
    if old_airtable_test_adj_records.empty:
        return new_airtable_test_adj_records

    # Add test adjustment data to old_test_adj_records from database
    old_airtable_record_ids = old_airtable_test_adj_records['airtable_record_id'].unique()

    # Query record ids in our database
    with db_session() as session:
        old_db_test_adj_records = session.query(DashboardSource.adj_prevalence,
                                                DashboardSource.adj_prev_ci_lower,
                                                DashboardSource.adj_prev_ci_upper,
                                                ResearchSource.adj_sensitivity,
                                                ResearchSource.adj_specificity,
                                                ResearchSource.ind_eval_type,
                                                ResearchSource.airtable_record_id) \
            .join(ResearchSource, ResearchSource.source_id == DashboardSource.source_id, isouter=True) \
            .filter(ResearchSource.airtable_record_id.in_(old_airtable_record_ids)).all()
        old_db_test_adj_records = [q._asdict() for q in old_db_test_adj_records]
        old_db_test_adj_records = pd.DataFrame(data=old_db_test_adj_records)

    # Join old_airtable_test_adj_records with old_db_adjusted_records
    old_airtable_test_adj_records = \
        old_airtable_test_adj_records.join(old_db_test_adj_records.set_index('airtable_record_id'),
                                           on='airtable_record_id')

    # Concat the old and new airtable test adj records
    airtable_master_data = pd.concat([new_airtable_test_adj_records, old_airtable_test_adj_records])
    return airtable_master_data
