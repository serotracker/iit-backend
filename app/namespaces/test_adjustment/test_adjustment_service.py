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

from app.utils.test_adjustment import bastos_estimates, testadj_model_code


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


class TestAdjHandler:
    def __init__(self, model_code=testadj_model_code, model_name='testadj_binomial_se_sp',
                 execution_params={}):
        self.TESTADJ_MODEL = self.get_stan_model_cache(model_code=model_code, model_name=model_name)
        self.TESTADJ_MODEL_NAME = model_name
        # Parse execution params
        self.n_iter = execution_params.get('n_iter', 2000)
        self.n_chains = execution_params.get('n_chains', 4)
        self.return_fit = execution_params.get('return_fit', False)
        self.trials_lim = execution_params.get('trials_lim', 5)
        self.modelsets_lim = execution_params.get('modelsets_lim', 3)

    # make sure to gitignore model caches, because the model needs to be compiled separately
    # on each machine - it is system-specific C++ code
    def get_stan_model_cache(self, model_code: str, model_name: str = 'anon_model', **kwargs: Dict) -> pystan.StanModel:
        """Use just as you would `pystan.StanModel`"""

        # Create filepath of cached model
        code_hash = md5(model_code.encode('ascii')).hexdigest()
        cache_fn = f'app/namespaces/test_adjustment/stanmodelcache-{model_name}-{code_hash}.pkl'
        arviz
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
        # Calculate adapt_delta param
        if model_params['n_sp'] < 10 or model_params['n_se'] < 10  \
                or model_params['y_sp'] < 5 or model_params['y_se'] < 5:
            adapt_delta = 0.99
        else:
            adapt_delta = 0.8

        # Construct init param dict
        init_one_chain = {
            'prev': model_params['y_prev_obs'] / model_params['n_prev_obs'],
            'sens': model_params['y_se'] / model_params['n_se'],
            'spec': model_params['y_sp'] / model_params['n_sp']
        }

        # pystan requires initial values to be expressed in a list of dicts, one dict for each chain
        init = [init_one_chain] * self.n_chains

        fit = self.TESTADJ_MODEL.sampling(data=model_params,
                                          iter=self.n_iter,
                                          chains=self.n_chains,
                                          control={'adapt_delta': adapt_delta},
                                          check_hmc_diagnostics=False,
                                          init=init)

        summary = fit.summary()
        summary_df = pd.DataFrame(data=summary['summary'],
                                  index=summary['summary_rownames'],
                                  columns=summary['summary_colnames'])

        samples = fit.extract(pars='prev', permuted=True)['prev']

        summary_df_parsed = summary_df.loc['prev', ['50%', '2.5%', '97.5%']]
        summary_df_parsed['samples'] = samples
        summary_df_parsed['fit'] = fit

        diagnostics = pystan.diagnostics.check_hmc_diagnostics(fit)

        satisfactory_model_found = diagnostics['n_eff'] and diagnostics['Rhat']
        return summary_df_parsed, satisfactory_model_found

    def pystan_adjust(self, model_params: Dict, execution_params: Dict = {}) -> Union[Tuple, pystan.StanModel]:
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
            # Attempt to fit a model
            summary_df_parsed, satisfactory_model_found = self.fit_one_pystan_model(model_params)

            # If model is not satisfactory, try 4 more times
            n_trials = 1
            while not satisfactory_model_found:
                summary_df_parsed, satisfactory_model_found = self.fit_one_pystan_model(model_params)
                # If number of attempts exceeded, return Nones
                n_trials += 1
                if n_trials >= self.trials_lim:
                    print('no models met the HMC diagnostics in {trials_lim} trials')
                    return None, None, None

            # get model result
            model_result = summary_df_parsed
            lower, upper = arviz.hdi(model_result['samples'], credible_interval_size)
            best_fit = model_result['fit']

            try:
                raw_prev = model_params['y_prev_obs'] / model_params['n_prev_obs']
                bounded = result_is_bounded(model_result, raw_prev)
            except (ZeroDivisionError, ValueError):
                return None, None, None

            satisfactory_model_set_found = bounded

            n_modelsets += 1
            if n_modelsets > self.modelsets_lim:
                return None, None, None

        if self.return_fit:
            return best_fit
        else:
            return lower, model_result, upper

    def get_adjusted_estimate(self, test_adj, ind_se, ind_sp, ind_se_n, ind_sp_n,
                              se_n, sp_n, sensitivity, specificity, test_validation,
                              test_type, denominator_value, serum_pos_prevalence) -> Tuple:
        # initialize adj_type
        adj_type = None

        # unadjusted estimate available and thus prioritized in estimate selection code
        if pd.isna(test_adj):

            # Independent evaluation is available
            if pd.notna(ind_se) and pd.notna(ind_sp):
                adj_type = 'FINDDx / MUHC independent evaluation'
                # Also note these must be divided by 100
                se = ind_se
                sp = ind_sp
                output_se_n = float(ind_se_n) * 100 if ind_se_n is not None else 30
                output_sp_n = float(ind_sp_n) * 100 if ind_sp_n is not None else 80

            # Author evaluation is available
            elif pd.notna(se_n) and pd.notna(sp_n) and \
                    pd.notna(sensitivity) and pd.notna(specificity):
                if test_validation and \
                        'Validated by independent authors/third party/non-developers' in test_validation:
                    adj_type = 'Author-reported independent evaluation'
                else:
                    adj_type = 'Test developer / manufacturer evaluation'
                se = sensitivity
                sp = specificity
                output_se_n = se_n if pd.notna(se_n) else 30
                output_sp_n = sp_n if pd.notna(sp_n) else 80

            # Manufacturer evaluation is available
            elif pd.notna(sensitivity) and pd.notna(specificity):
                adj_type = 'Test developer / manufacturer evaluation'
                se = sensitivity
                sp = specificity
                # per FDA minimum requirements https://www.fda.gov/medical-devices/
                # coronavirus-disease-2019-covid-19-emergency-use-authorizations-medical-devices/
                # eua-authorized-serology-test-performance
                output_se_n, output_sp_n = 30, 80

            else:
                # if there is no matched adjusted estimate available:
                found_test_type = False
                for standard_test_type in ['LFIA', 'CLIA', 'ELISA']:
                    if test_type and test_type == standard_test_type:
                        se = bastos_estimates[standard_test_type]['se']['50']
                        sp = bastos_estimates[standard_test_type]['sp']['50']
                        output_se_n = bastos_estimates[standard_test_type]['se']['n']
                        output_sp_n = bastos_estimates[standard_test_type]['sp']['n']
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
                print('ADJUSTING ESTIMATE', adj_type)
                model_params = dict(
                    n_prev_obs=int(denominator_value),
                    y_prev_obs=int(
                        serum_pos_prevalence * denominator_value),
                    n_se=int(output_se_n),
                    y_se=int(output_se_n * se),
                    n_sp=int(output_sp_n),
                    y_sp=int(output_sp_n * sp)
                )
                lower, adj_prev, upper = self.pystan_adjust(model_params)
                if pd.isna(adj_prev):
                    print(f'FAILED TO ADJUST ESTIMATE')

        else:
            adj_type = 'Used author-adjusted estimate'
            adj_prev = serum_pos_prevalence
            se = sensitivity
            sp = specificity

            lower, upper = proportion_confint(int(denominator_value * serum_pos_prevalence),
                                              denominator_value, alpha=0.05, method='jeffreys')
        return adj_prev, se, sp, adj_type, lower, upper
