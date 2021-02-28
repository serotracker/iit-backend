# monte-carlo version of RG estimator,
# accounting for uncertainty in se and sp estimates
from numpy import nan
from math import log
from statsmodels.stats.proportion import proportion_confint
import pandas as pd
import pystan
import arviz

from marshmallow import Schema, fields, ValidationError

# To resolve error when running multiple chains at once:
# https://discourse.mc-stan.org/t/new-to-pystan-always-get-this-error-when-attempting-to-sample-modulenotfounderror-no-module-named-stanfit4anon-model/19288/3
import multiprocessing
multiprocessing.set_start_method("fork")

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

# Bastos 2020 in BMJ provided a SR&MA of serological test diagnostic accuracy
# https://www.bmj.com/content/370/bmj.m2516
# we use their provided Se and Sp figures when independent evaluations are not available in our data
# and infer their distributions from the total number of samples provided

bastos_estimates = {
    'ELISA': {
        'se': {
            '50': 75.6,
            '2.5': 84.3,
            '97.5': 90.9,
            'n': 766
        },
        'sp': {
            '50': 97.6,
            '2.5': 93.2,
            '97.5': 99.4,
            'n': 1109
        }
    },
    'LFIA': {
        'se': {
            '50': 66.0,
            '2.5': 49.3,
            '97.5': 79.3,
            'n': 2660
        },
        'sp': {
            '50': 96.6,
            '2.5': 94.3,
            '97.5': 98.2,
            'n': 2874
        }
    },
    'CLIA': {
        'se': {
            '50': 97.8,
            '2.5': 46.2,
            '97.5': 100,
            'n': 375
        },
        'sp': {
            '50': 97.8,
            '2.5': 62.9,
            '97.5': 99.9,
            'n': 2804
        }
    }
}

# rescale seroprevalence data from percentages to proportion
bastos_estimates = {test_type: {
    char: {prop: value / 100 if prop != 'n' else value for prop, value in char_di.items()}
    for char, char_di in test_type_di.items()}
    for test_type, test_type_di in bastos_estimates.items()}

# TODO: Figure out if we can serialize this
def build_testadj_model():
    # specify and compile stan model
    testadj_model_code = """
    data {
        int<lower = 0> n_prev_obs;
        int<lower = 0> y_prev_obs;
        int<lower = 0> n_se;
        int<lower = 0> y_se;
        int<lower = 0> n_sp;
        int<lower = 0> y_sp;
    }
    parameters {
        real<lower = 0, upper = 1> prev;
        real<lower = 0, upper = 1> sens;
        real<lower = 0, upper = 1> spec;
    }
    model {
        real prev_obs = prev * sens + (1 - prev) * (1 - spec);
        y_prev_obs ~ binomial(n_prev_obs, prev_obs);
        y_se ~ binomial(n_se, sens);
        y_sp ~ binomial(n_sp, spec);
    }
    """

    return pystan.StanModel(model_code=testadj_model_code)

def fit_one_pystan_model(testadj_model, model_params, n_iter, n_chains):
    fit = testadj_model.sampling(data=model_params, iter=n_iter, chains=n_chains,
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

    satisfactory_model = all(diagnostics.values())

    return summary_df_parsed, satisfactory_model

def pystan_adjust(testadj_model, model_params, execution_params={}):
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
                summary_df_parsed, satisfactory_model = fit_one_pystan_model(testadj_model, model_params, n_iter, n_chains)
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

        lower, upper = arviz.hpd(median_run['samples'], credible_interval_size)
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
    # unadjusted estimate available and thus prioritized in estimate selection code
    if pd.isna(estimate['TEST_ADJ']):

        # Independent evaluation is available
        if estimate['ind_se'].notnull() & estimate['ind_sp'].notnull():
            adj_type = 'FINDDx / MUHC independent evaluation'
            se = estimate['ind_se']
            sp = estimate['ind_sp']
            se_n = estimate['ind_se_n'] if pd.notna(estimate['ind_se_n']) else 30
            sp_n = estimate['ind_sp_n'] if pd.notna(estimate['ind_sp_n']) else 80

        # Author evaluation is available
        elif estimate['se_n'].notnull() & estimate['sp_n'].notnull() & estimate['sensitivity'].notnull() & estimate['specificity'].notnull():
            if 'Validated by independent authors/third party/non-developers' in estimate['test_validation']:
                adj_type = 'Author-reported independent evaluation'
            else:
                adj_type = 'Test developer / manufacturer evaluation'
            se = estimate['sensitivity']
            sp = estimate['specificity']
            se_n = estimate['se_n'] if pd.notna(estimate['se_n']) else 30
            sp_n = estimate['sp_n'] if pd.notna(estimate['sp_n']) else 80

        # Manufacturer evaluation is available
        elif estimate['sensitivity'].notnull() & estimate['specificity'].notnull():
            adj_type = 'Test developer / manufacturer evaluation'
            se = estimate['sensitivity']
            sp = estimate['specificity']
            # per FDA minimum requirements https://www.fda.gov/medical-devices/coronavirus-disease-2019-covid-19-emergency-use-authorizations-medical-devices/eua-authorized-serology-test-performance
            se_n, sp_n = 30, 80

        else:
            # if there is no matched adjusted estimate available:
            for test_type in ['LFIA', 'CLIA', 'ELISA', None]:
                if test_type in estimate['test_types']:
                    se = bastos_estimates[test_type]['se']['50']
                    sp = bastos_estimates[test_type]['sp']['50']
                    se_n = bastos_estimates[test_type]['se']['n']
                    sp_n = bastos_estimates[test_type]['sp']['n']
                    adj_type = 'Used Bastos SR/MA data; no sens, spec, or author adjustment available'
                    break

                if pd.isna(test_type):
                    adj_type = 'No data altogether'
                    break

        if adj_type == 'No data altogether':
            adj_prev = nan
            se = nan
            sp = nan
            lower = nan
            upper = nan
        else:
            print(f'ADJUSTING ESTIMATE AT INDEX {estimate.name}')
            lower, adj_prev, upper = pystan_adjust(n_prev_obs=int(estimate['denominator_value']),
                                                   y_prev_obs=int(
                                                       estimate['serum_pos_prevalence'] * estimate['denominator_value']),
                                                   n_se=int(se_n),
                                                   y_se=int(se_n * se),
                                                   n_sp=int(sp_n),
                                                   y_sp=int(sp_n * sp),
                                                   n_iter=n_iter,
                                                   n_chains=n_chains)
            if pd.isna(adj_prev):
                print(f'FAILED TO ADJUST ESTIMATE AT INDEX {estimate.name}')

    else:
        adj_type = 'Used author-adjusted estimate'
        adj_prev = estimate['serum_pos_prevalence']
        se = estimate['sensitivity']
        sp = estimate['specificity']

        lower, upper = proportion_confint(int(estimate['denominator_value'] * estimate['serum_pos_prevalence']),
                                          estimate['denominator_value'], alpha=0.1, method='jeffreys')

    estimate['adj_prevalence'] = adj_prev
    estimate['adj_sensitivity'] = se
    estimate['adj_specificity'] = sp
    estimate['ind_eval_type'] = adj_type
    estimate['adj_prev_ci_lower'] = lower
    estimate['adj_prev_ci_upper'] = upper

    return estimate


if __name__ == '__main__':

    # use santa clara and denmark findings as sample data
    bendavid_data = {
        'n_prev_obs': 3330,
        'y_prev_obs': 50,
        'n_se': 122,
        'y_se': 103,
        'n_sp': 401,
        'y_sp': 399
    }

    denmark_data_1 = {
        'n_prev_obs': 20640,
        'y_prev_obs': 413,
        'n_se': 59,
        'y_se': 40,
        'n_sp': 14,
        'y_sp': 9
    }

    testadj_model = build_testadj_model()
    execution_params = {"return_fit": True}

    print(pystan_adjust(testadj_model, bendavid_data, execution_params))
    print(pystan_adjust(testadj_model, denmark_data_1, execution_params))
