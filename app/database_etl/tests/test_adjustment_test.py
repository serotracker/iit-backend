from app.database_etl.test_adjustment_handler import TestAdjHandler, testadj_model_code
import os
import pandas as pd
import pytest

# Pytest will assert a failure if test adj takes too long (over 60 seconds)
@pytest.mark.timeout(60)
def test_adjustment_on_test_set():
    csv_path = os.path.abspath(os.path.dirname(__file__)) + '/../test_adjustment_handler/test_adj_test_set.csv'
    records_df = pd.read_csv(csv_path)
    # ensure n_chains = 1 so that we don't need to multiprocess (easier for github CI to run)
    testadjHandler = TestAdjHandler(model_code=testadj_model_code, model_name='testadj_binomial_se_sp',
                                    execution_params={'n_chains': 1})

    # Convert numeric cols to float (some of these come out of airtable as strings so need to standardize types)
    float_cols = ['ind_se', 'ind_sp', 'ind_se_n', 'ind_sp_n', 'se_n', 'sp_n', 'sensitivity', 'specificity',
                  'denominator_value', 'serum_pos_prevalence']
    records_df[float_cols] = records_df[float_cols].astype(float)

    # Call test adjustment
    records_df['adj_prevalence'], records_df['adj_sensitivity'], records_df['adj_specificity'], \
    records_df['ind_eval_type'], records_df['adj_prev_ci_lower'], records_df['adj_prev_ci_upper'] = \
        zip(*records_df.apply(lambda row: testadjHandler.get_adjusted_estimate(row), axis=1))

    # Check that at least one of the records without previously adjusted vals was able to be adjusted
    prev_unadj_records = records_df[records_df["ind_eval_type"] != 'Used author-adjusted estimate']

    assert prev_unadj_records['adj_prevalence'].notna().sum() > 0