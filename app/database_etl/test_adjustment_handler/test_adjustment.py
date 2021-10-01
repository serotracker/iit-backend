# monte-carlo version of RG estimator,
# accounting for uncertainty in se and sp estimates
from math import log

import pandas as pd
from marshmallow import Schema, fields, ValidationError

from app.database_etl.test_adjustment_handler import testadj_model_code
from app.namespaces.test_adjustment import TestAdjHandler
from app.serotracker_sqlalchemy import db_session, ResearchSource, DashboardSource
from app.database_etl.airtable_records_handler import batch_update_airtable_records


def logit(p, tol=1e-3):
    # logit function; well defined for p in open interval (0,1)
    
    # constrain the probability to the range [tol, 1-tol]
    # to avoid NaNs if p = 0 or p = 1
    p = max(p, tol)
    p = min(p, 1 - tol)
    
    # return the logit of the constrained probability
    return log(p / (1 - p))


def result_is_bounded(median_adj_prev, raw_prev):
    
    # check whether the adjusted result is close to the raw value
    # e.g., log odds within 1 
    logit_delta = logit(median_adj_prev) - logit(raw_prev)
    adjusted_closeto_raw = abs(logit_delta) < 1

    # permit the adjusted result if adjusted and raw are both < 0.5
    # or if both are > 0.5    
    both_below_maxsmall = (median_adj_prev <= 0.5) and (raw_prev <= 0.5)
    both_above_minbig = (median_adj_prev >= 0.5) and (raw_prev >= 0.5)
    
    return (adjusted_closeto_raw or both_below_maxsmall or both_above_minbig)


def validate_against_schema(input_payload, schema):
    try:
        payload = schema.load(input_payload)
    except ValidationError as err:
        return err.messages
    return payload


class ModelParamsSchema(Schema):
    n_prev_obs = fields.Integer()
    y_prev_obs = fields.Float()
    n_se = fields.Integer()
    y_se = fields.Float()
    n_sp = fields.Integer()
    y_sp = fields.Float()


def run_on_test_set(model_code: str = testadj_model_code, model_name: str = 'testadj_binomial_se_sp') -> pd.DataFrame:
    records_df = pd.read_csv('test_adj_test_set.csv')
    testadjHandler = TestAdjHandler(model_code=model_code, model_name=model_name)

    # Write to csv
    records_df['adj_prevalence'], records_df['adj_sensitivity'], records_df['adj_specificity'], \
    records_df['ind_eval_type'], records_df['adj_prev_ci_lower'], records_df['adj_prev_ci_upper'] = \
        zip(*records_df.apply(lambda row: testadjHandler.get_adjusted_estimate(row), axis=1))
    return records_df


def add_test_adjustments(df: pd.DataFrame) -> pd.DataFrame:
    # Query record ids in our database
    with db_session() as session:
        total_db_records = session.query(DashboardSource.serum_pos_prevalence,
                                         DashboardSource.test_adj,
                                         DashboardSource.sensitivity,
                                         DashboardSource.specificity,
                                         DashboardSource.test_type,
                                         DashboardSource.denominator_value,
                                         DashboardSource.adj_prevalence,
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
        test_adj_handler = TestAdjHandler()
        new_airtable_test_adj_records['adj_prevalence'], \
        new_airtable_test_adj_records['adj_sensitivity'], \
        new_airtable_test_adj_records['adj_specificity'], \
        new_airtable_test_adj_records['ind_eval_type'], \
        new_airtable_test_adj_records['adj_prev_ci_lower'], \
        new_airtable_test_adj_records['adj_prev_ci_upper'] = \
            zip(*new_airtable_test_adj_records.apply(
                lambda x: test_adj_handler.get_adjusted_estimate(test_adj=x['test_adj'],
                                                                 ind_se=x['ind_se'],
                                                                 ind_sp=x['ind_sp'],
                                                                 ind_se_n=x['ind_se_n'],
                                                                 ind_sp_n=x['ind_sp_n'],
                                                                 se_n=x['se_n'],
                                                                 sp_n=x['sp_n'],
                                                                 sensitivity=x['sensitivity'],
                                                                 specificity=x['specificity'],
                                                                 test_validation=x['test_validation'],
                                                                 test_type=x['test_type'],
                                                                 denominator_value=x['denominator_value'],
                                                                 serum_pos_prevalence=x['serum_pos_prevalence']),
                axis=1))

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

    # Drop the test adjustment data that is currently in airtable, and keep the one int he DB
    old_airtable_test_adj_records = old_airtable_test_adj_records.drop(columns=['adj_prevalence',
                                                                                'adj_prev_ci_lower',
                                                                                'adj_prev_ci_upper',
                                                                                'adj_sensitivity',
                                                                                'adj_specificity',
                                                                                'ind_eval_type'])

    # Join old_airtable_test_adj_records with old_db_adjusted_records
    old_airtable_test_adj_records = \
        old_airtable_test_adj_records.join(old_db_test_adj_records.set_index('airtable_record_id'),
                                           on='airtable_record_id')

    # Concat the old and new airtable test adj records
    airtable_master_data = pd.concat([new_airtable_test_adj_records, old_airtable_test_adj_records])

    batch_update_airtable_records(new_airtable_test_adj_records, ['Adjusted serum positive prevalence', ])
    return airtable_master_data
