# monte-carlo version of RG estimator,
# accounting for uncertainty in se and sp estimates
from numpy import nan
from math import log
from statsmodels.stats.proportion import proportion_confint
import pandas as pd
import pystan
import arviz

import pickle
from hashlib import md5

from app.utils import get_filtered_records
from app.namespaces.data_provider.data_provider_service import jitter_pins
from app.database_etl.test_adjustment_handler import bastos_estimates, testadj_model_code

from marshmallow import Schema, fields, ValidationError
import multiprocessing

# make sure to gitignore model caches, because the model needs to be compiled separately
# on each machine - it is system-specific C++ code 
def StanModel_cache(model_code, model_name = 'anon_model', **kwargs):
    """Use just as you would `pystan.StanModel`"""
    
    code_hash = md5(model_code.encode('ascii')).hexdigest()
    cache_fn = f'stanmodelcache-{model_name}-{code_hash}.pkl'
    
    try:
        stanmodel = pickle.load(open(cache_fn, 'rb'))
        print(f"Using cached StanModel at filepath {cache_fn}")
    except:
        stanmodel = pystan.StanModel(model_code = model_code,
                                     model_name = model_name, 
                                     **kwargs)
        with open(cache_fn, 'wb') as f:
            pickle.dump(sm, f)
            
    return sm

TESTADJ_MODEL = StanModel_cache(model_code = testadj_model_code,
                                model_name = 'testadj_binomial_se_sp')

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

def fit_one_pystan_model(model_params, n_iter, n_chains):
    fit = TESTADJ_MODEL.sampling(data=model_params, iter=n_iter, chains=n_chains,
                                 control={'adapt_delta': 0.95},
                                 check_hmc_diagnostics=False)

    summary = fit.summary()
    summary_df = pd.DataFrame(data=summary['summary'],
                              index=summary['summary_rownames'],
                              columns=summary['summary_colnames'])

    samples = fit.extract(pars='prev', permuted=True)['prev']

    summary_df_parsed = summary_df.loc['prev', ['50%', '2.5%', '97.5%']]
    summary_df_parsed['samples'] = samples
    summary_df_parsed['fit'] = fit

    diagnostics = pystan.diagnostics.check_hmc_diagnostics(fit)

    satisfactory_model_found = all(diagnostics.values())

    return summary_df_parsed, satisfactory_model_found

def pystan_adjust(model_params, execution_params={}):
    # Parse execution options
    n_iter = execution_params.get('n_iter', 2000)
    n_chains = execution_params.get('n_chains', 4)
    # unclear if required in prod
    return_fit = execution_params.get('return_fit', False)
    n_replicates = execution_params.get('n_replicates', 5)
    trials_lim = execution_params.get('trials_lim', 100)
    modelsets_lim = execution_params.get('modelsets_lim', 3)
    if n_replicates % 2 != 1:
        raise ValueError(f'n_replicates must be odd')
    credible_interval_size = execution_params.get('credible_interval_size', 0.95)

    # Validate model_params using marshmallow
    try:
        ModelParamsSchema().load(model_params)
    except ValidationError as err:
        print("Error: ", err.messages)
        return None, None, None

    satisfactory_model_set_found = False
    n_modelsets = 0

    while not satisfactory_model_set_found:
        satisfactory_model_set = []
        for _ in range(n_replicates):
            n_trials = 0
            satisfactory_model_found = False

            while not satisfactory_model_found:
                # Attempt to fit a model
                summary_df_parsed, satisfactory_model_found = fit_one_pystan_model(model_params, n_iter, n_chains)
                # If number of attempts exceeded, return Nones
                n_trials += 1
                if n_trials >= trials_lim:
                    print('no models met the HMC diagnostics in {trials_lim} trials')
                    return None, None, None

            satisfactory_model_set.append(summary_df_parsed)

        satisfactory_models_df = pd.DataFrame(satisfactory_model_set)

        # see whether all results are within 10% of median; if not, rerun
        model_medians = satisfactory_models_df['50%']
        median = model_medians.median()
        consistent_results_found = model_medians.between(0.9 * median, 1.1 * median).all()
        median_run = satisfactory_models_df[satisfactory_models_df['50%'] == median].iloc[0]

        lower, upper = arviz.hdi(median_run['samples'], credible_interval_size)
        best_fit = median_run['fit']

        try:
            raw_prev = model_params['y_prev_obs'] / model_params['n_prev_obs']
            log_delta = log(median + 1e-3, 10) - log(raw_prev + 1e-3, 10)
            median_is_bounded = abs(log_delta) < 1
        except (ZeroDivisionError, ValueError):
            return None, None, None

        satisfactory_model_set_found = consistent_results_found and median_is_bounded

        n_modelsets += 1
        if n_modelsets > modelsets_lim:
            return None, None, None

    if return_fit:
        return best_fit
    else:
        return lower, median, upper


def get_adjusted_estimate(estimate, n_iter=2000, n_chains=4):
    # initialize adj_type
    adj_type = None

    # unadjusted estimate available and thus prioritized in estimate selection code
    if pd.isna(estimate['test_adj']):

        # Independent evaluation is available
        if pd.notna(estimate['ind_se']) and pd.notna(estimate['ind_sp']):
            adj_type = 'FINDDx / MUHC independent evaluation'
            # Also note these must be divided by 100
            se = estimate['ind_se'] / 100
            sp = estimate['ind_sp'] / 100
            # Note: for some reason ind_se_n and ind_sp_n are floats in the DB
            # See line 51 in airtable_records_formatter.py to see where the conversion is happening in the ETL
            # Test adjustment expects them to be integers so we gotta convert back
            se_n = estimate['ind_se_n']*100 if pd.notna(estimate['ind_se_n']) else 30
            sp_n = estimate['ind_sp_n']*100 if pd.notna(estimate['ind_sp_n']) else 80

        # Author evaluation is available
        elif pd.notna(estimate['se_n']) and pd.notna(estimate['sp_n']) and \
                pd.notna(estimate['sensitivity']) and pd.notna(estimate['specificity']):
            if estimate['test_validation'] and 'Validated by independent authors/third party/non-developers' in estimate['test_validation']:
                adj_type = 'Author-reported independent evaluation'
            else:
                adj_type = 'Test developer / manufacturer evaluation'
            se = estimate['sensitivity']
            sp = estimate['specificity']
            se_n = estimate['se_n'] if pd.notna(estimate['se_n']) else 30
            sp_n = estimate['sp_n'] if pd.notna(estimate['sp_n']) else 80

        # Manufacturer evaluation is available
        elif pd.notna(estimate['sensitivity']) and pd.notna(estimate['specificity']):
            adj_type = 'Test developer / manufacturer evaluation'
            se = estimate['sensitivity']
            sp = estimate['specificity']
            # per FDA minimum requirements https://www.fda.gov/medical-devices/coronavirus-disease-2019-covid-19-emergency-use-authorizations-medical-devices/eua-authorized-serology-test-performance
            se_n, sp_n = 30, 80

        else:
            # if there is no matched adjusted estimate available:
            found_test_type = False
            for test_type in ['LFIA', 'CLIA', 'ELISA']:
                if estimate['test_type'] and test_type == estimate['test_type']:
                    se = bastos_estimates[test_type]['se']['50']
                    sp = bastos_estimates[test_type]['sp']['50']
                    se_n = bastos_estimates[test_type]['se']['n']
                    sp_n = bastos_estimates[test_type]['sp']['n']
                    adj_type = 'Used Bastos SR/MA data; no sens, spec, or author adjustment available'
                    found_test_type = True
                    break
            if not found_test_type:
                adj_type = 'No data altogether'

        if adj_type == 'No data altogether':
            adj_prev = nan
            se = nan
            sp = nan
            lower = nan
            upper = nan
        else:
            print(f'ADJUSTING ESTIMATE AT INDEX {estimate.name}', adj_type)
            model_params = dict(
                n_prev_obs=int(estimate['denominator_value']),
                y_prev_obs=int(
                    estimate['serum_pos_prevalence'] * estimate['denominator_value']),
                n_se=int(se_n),
                y_se=int(se_n * se),
                n_sp=int(sp_n),
                y_sp=int(sp_n * sp)
            )
            execution_params = dict(
                n_iter=n_iter,
                n_chains=n_chains
            )
            lower, adj_prev, upper = pystan_adjust(model_params, execution_params)
            if pd.isna(adj_prev):
                print(f'FAILED TO ADJUST ESTIMATE AT INDEX {estimate.name}')

    else:
        adj_type = 'Used author-adjusted estimate'
        adj_prev = estimate['serum_pos_prevalence']
        se = estimate['sensitivity']
        sp = estimate['specificity']

        lower, upper = proportion_confint(int(estimate['denominator_value'] * estimate['serum_pos_prevalence']),
                                          estimate['denominator_value'], alpha=0.1, method='jeffreys')

    return adj_prev, se, sp, adj_type, lower, upper

def test_code():
    # use santa clara and denmark findings as sample data
    bendavid_data = {
        'n_prev_obs': 3330,
        'y_prev_obs': 50,
        'n_se': 122,
        'y_se': 103,
        'n_sp': 401,
        'y_sp': 399
    }

    denmark_data = {
        'n_prev_obs': 20640,
        'y_prev_obs': 413,
        'n_se': 59,
        'y_se': 40,
        'n_sp': 14,
        'y_sp': 9
    }

    execution_params = dict(
        n_iter=2000,
        n_chains=4
    )

    print(pystan_adjust(bendavid_data, execution_params))
    print(pystan_adjust(denmark_data, execution_params))


if __name__ == '__main__':
    # To resolve error when running multiple chains at once:
    # https://discourse.mc-stan.org/t/new-to-pystan-always-get-this-error-when-attempting-to-sample-modulenotfounderror-no-module-named-stanfit4anon-model/19288/3
    multiprocessing.set_start_method("fork")

    test_code()

    """
    # Get records
    records = get_filtered_records(research_fields=True, filters=None, columns=None, start_date=None,
                                   end_date=None, prioritize_estimates=False)[:10]
    records = jitter_pins(records)
    records_df = pd.DataFrame(records)

    # Turn lists into comma sep strings
    cols = ['city', 'state', 'test_manufacturer', 'antibody_target', 'isotypes_reported']
    for col in cols:
        records_df[col] = records_df[col].apply(lambda x: ",".join(x))

    # Clean df
    records_df['source_id'] = records_df['source_id'].apply(lambda x: str(x))
    records_df = records_df.replace('[', '')
    records_df = records_df.replace(']', '')

    # Write to csv
    records_df['adj_prevalence'], records_df['adj_sensitivity'], records_df['adj_specificity'], \
    records_df['ind_eval_type'], records_df['adj_prev_ci_lower'], records_df['adj_prev_ci_upper'] = \
        zip(*records_df.apply(lambda row: get_adjusted_estimate(row), axis=1))

    records_df.to_csv("test_adj.csv")
    print("COMPLETED")
    """