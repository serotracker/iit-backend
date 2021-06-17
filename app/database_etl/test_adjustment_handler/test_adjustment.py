# monte-carlo version of RG estimator,
# accounting for uncertainty in se and sp estimates
import pickle
from math import log
from hashlib import md5
from typing import Dict, Tuple, Union

import pandas as pd
import pystan
import arviz
from statsmodels.stats.proportion import proportion_confint
from marshmallow import Schema, fields, ValidationError

from app.database_etl.test_adjustment_handler import bastos_estimates, testadj_model_code

def logit(p, tol = 1e-3):
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


class TestAdjHandler:
    def __init__(self, model_code=testadj_model_code, model_name='testadj_binomial_se_sp',
                 execution_params={}):
        self.TESTADJ_MODEL = self.get_stan_model_cache(model_code=model_code, model_name=model_name)
        self.TESTADJ_MODEL_NAME = model_name
        # Parse execution params
        self.n_iter = execution_params.get('n_iter', 2000)
        self.n_chains = execution_params.get('n_chains', 4)
        self.return_fit = execution_params.get('return_fit', False)
        self.n_replicates = execution_params.get('n_replicates', 5)
        self.trials_lim = execution_params.get('trials_lim', 100)
        self.modelsets_lim = execution_params.get('modelsets_lim', 3)

    # make sure to gitignore model caches, because the model needs to be compiled separately
    # on each machine - it is system-specific C++ code
    def get_stan_model_cache(self, model_code: str, model_name: str = 'anon_model', **kwargs: Dict) -> pystan.StanModel:
        """Use just as you would `pystan.StanModel`"""

        # Create filepath of cached model
        code_hash = md5(model_code.encode('ascii')).hexdigest()
        cache_fn = f'stanmodelcache-{model_name}-{code_hash}.pkl'

        # Try to load cached model
        try:
            cached_model = pickle.load(open(cache_fn, 'rb'))
            print(f"Using cached StanModel at filepath {cache_fn}")

        # Otherwise create the model and cache it
        except FileNotFoundError:
            cached_model = pystan.StanModel(model_code=model_code, model_name=model_name, **kwargs)
            with open(cache_fn, 'wb') as f:
                pickle.dump(cached_model, f)
        return cached_model

    def fit_one_pystan_model(self, model_params: Dict) -> Tuple:
        
        # Need to change the Hyperparameters in this part given the
        # the model Data
        
        #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
        #                          Start of New Code                         #
        #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
        
        if (model_params['n_se'] < 10 or model_params['y_se'] < 10 or model_params['n_sp'] < 5 or model_params['y_sp'] < 5):
            adpt_delt = 0.99
            self.n_iter = 12000
        else:
            adpt_delt = 0.80
            self.n_iter = 2000
                
        
        
        
        
        #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
        #                            End of New Code                         #
        #*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#*
        
        
        fit = self.TESTADJ_MODEL.sampling(data=model_params,
                                          iter=self.n_iter,
                                          chains=self.n_chains,
                                          control={'adapt_delta': adpt_delt},
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

    def pystan_adjust(self, model_params: Dict, execution_params: Dict = {}) -> Union[Tuple, pystan.StanModel]:
        if self.n_replicates % 2 != 1:
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
            for _ in range(self.n_replicates):
                n_trials = 0
                satisfactory_model_found = False

                while not satisfactory_model_found:
                    # Attempt to fit a model
                    summary_df_parsed, satisfactory_model_found = self.fit_one_pystan_model(model_params)
                    # If number of attempts exceeded, return Nones
                    n_trials += 1
                    if n_trials >= self.trials_lim:
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
                bounded = result_is_bounded(median, raw_prev)
            except (ZeroDivisionError, ValueError):
                return None, None, None

            satisfactory_model_set_found = consistent_results_found and bounded

            n_modelsets += 1
            if n_modelsets > self.modelsets_lim:
                return None, None, None

        if self.return_fit:
            return best_fit
        else:
            return lower, median, upper

    def get_adjusted_estimate(self, estimate: pd.Series) -> Tuple:
        # initialize adj_type
        adj_type = None

        # unadjusted estimate available and thus prioritized in estimate selection code
        if pd.isna(estimate['test_adj']):

            # Independent evaluation is available
            if pd.notna(estimate['ind_se']) and pd.notna(estimate['ind_sp']):
                adj_type = 'FINDDx / MUHC independent evaluation'
                # Also note these must be divided by 100
                se = (estimate['ind_se']) / 100
                sp = (estimate['ind_sp']) / 100
                se_n = float(estimate['ind_se_n'][0]) * 100 if estimate['ind_se_n'] is not None else 30
                sp_n = float(estimate['ind_sp_n'][0]) * 100 if estimate['ind_sp_n'] is not None else 80

            # Author evaluation is available
            elif pd.notna(estimate['se_n']) and pd.notna(estimate['sp_n']) and \
                    pd.notna(estimate['sensitivity']) and pd.notna(estimate['specificity']):
                if estimate['test_validation'] and \
                        'Validated by independent authors/third party/non-developers' in estimate['test_validation']:
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
                # per FDA minimum requirements https://www.fda.gov/medical-devices/
                # coronavirus-disease-2019-covid-19-emergency-use-authorizations-medical-devices/
                # eua-authorized-serology-test-performance
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
                adj_prev = None
                se = None
                sp = None
                lower = None
                upper = None
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
                lower, adj_prev, upper = self.pystan_adjust(model_params)
                if pd.isna(adj_prev):
                    print(f'FAILED TO ADJUST ESTIMATE AT INDEX {estimate.name}')

        else:
            adj_type = 'Used author-adjusted estimate'
            adj_prev = estimate['serum_pos_prevalence']
            se = estimate['sensitivity']
            sp = estimate['specificity']

            lower, upper = proportion_confint(int(estimate['denominator_value'] * estimate['serum_pos_prevalence']),
                                              estimate['denominator_value'], alpha=0.05, method='jeffreys')
        return adj_prev, se, sp, adj_type, lower, upper


def run_on_test_set(model_code: str = testadj_model_code, model_name: str = 'testadj_binomial_se_sp') -> pd.DataFrame:
    records_df = pd.read_csv('test_adj_test_set.csv')
    testadjHandler = TestAdjHandler(model_code=model_code, model_name=model_name)

    # Write to csv
    records_df['adj_prevalence'], records_df['adj_sensitivity'], records_df['adj_specificity'], \
    records_df['ind_eval_type'], records_df['adj_prev_ci_lower'], records_df['adj_prev_ci_upper'] = \
        zip(*records_df.apply(lambda row: testadjHandler.get_adjusted_estimate(row), axis=1))
    return records_df
