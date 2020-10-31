from statistics import median
from math import log, sqrt, asin, exp, sin, cos, pi

import pandas as pd
from numpy import sign, quantile, isnan
from scipy.stats import hmean
from flask import current_app as app

Z_975 = 1.96
SP_ZERO_BLACKLIST = ['untransformed', 'logit']
pd.options.mode.chained_assignment = None


def calc_transformed_prevalence(p, N, method):
    if method == 'untransformed':
        return p
    elif method == 'logit':
        return log(p / (1 - p))
    elif method == 'arcsin':
        return asin(sqrt(p))
    elif method == 'double_arcsin_approx' or method == 'double_arcsin_precise':
        n = N * p
        return 0.5 * (asin(sqrt(n / (N + 1))) + asin(sqrt((n + 1) / (N + 1))))


def calc_transformed_variance(p, N, method):
    if method == 'untransformed':
        return p * (1 - p) / N
    elif method == 'logit':
        return 1 / (N * p) + 1 / (N * (1 - p))
    elif method == 'arcsin':
        return 1 / (4 * N)
    elif method == 'double_arcsin_approx' or method == 'double_arcsin_precise':
        return 1 / (4 * N + 2)


def back_transform_prevalence(t, n, method):
    if method == 'untransformed':
        if t < 0:
            return 0
        elif t > 1:
            return 1
        else:
            return t
    elif method == 'logit':
        return exp(t) / (exp(t) + 1)
    elif method == 'arcsin' or method == 'double_arcsin_approx':
        if t < 0:
            return 0
        elif t > pi / 2:
            return 1
        else:
            return sin(t) ** 2
    elif method == 'double_arcsin_precise':
        if t < 0:
            return 0
        elif t > pi / 2:
            return 1
        else:
            return 0.5 * (1 - sign(cos(2 * t)) * sqrt(1 - (sin(2 * t) + (sin(2 * t) - 2 * sin(2 * t)) / n) ** 2))


def calc_between_study_variance(records):
    q = sum(
        records['FIXED_WEIGHT'] * (records['TRANSFORMED_PREVALENCE'] - records['TRANSFORMED_POOLED_PREVALENCE']) ** 2)
    estimator_numerator = q - (records.shape[0] - 1)
    estimator_denominator = sum(records['FIXED_WEIGHT']) - sum((records['FIXED_WEIGHT']) ** 2) / sum(
        records['FIXED_WEIGHT'])
    if estimator_denominator == 0:
        return 0
    else:
        return max(0, estimator_numerator / estimator_denominator)


def get_valid_filtered_records(records, transformation):
    # Remove records based on criteria for prevalence and denominator fields
    filtered_records = records[(records['serum_pos_prevalence'].notna()) &
                               (records['denominator_value'].notna()) &
                               (records[
                                    'serum_pos_prevalence'] != 0 if transformation in SP_ZERO_BLACKLIST else True)]

    # If at least one record meets min denom criteria, filter out the rest that do not
    if (filtered_records['denominator_value'] >= app.config['MIN_DENOMINATOR']).any():
        filtered_records = filtered_records[filtered_records['denominator_value'] >= app.config['MIN_DENOMINATOR']]
    return filtered_records


def get_trans_pooled_prev_and_ci(weighted_prev_sum, weighted_sum, variance_sum):
    trans_pooled_prevalence = weighted_prev_sum / weighted_sum
    trans_conf_inter = [trans_pooled_prevalence - Z_975 * sqrt(variance_sum),
                        trans_pooled_prevalence + Z_975 * sqrt(variance_sum)]
    return trans_pooled_prevalence, trans_conf_inter


def get_pooled_prevalence_and_error(transformed_prev, overall_n, transformation, transformed_ci):
    pooled_prevalence = back_transform_prevalence(transformed_prev, overall_n, transformation)
    conf_inter = [back_transform_prevalence(i, overall_n, transformation) for i in transformed_ci]
    conf_inter = [max(conf_inter[0], 0), min(conf_inter[1], 1)]
    error = [abs(pooled_prevalence - i) for i in conf_inter]
    return pooled_prevalence, error


def get_return_body(prevalence, error, total_population, total_studies, countries_col):
    num_countries = len(countries_col.unique())
    body = {
            'seroprevalence_percent': prevalence * 100,
            'error_percent': [i * 100 for i in error],
            'total_N': total_population,
            'n_studies': total_studies,
            'countries': num_countries
            }
    return body


def calc_pooled_prevalence_for_subgroup(records, meta_transformation='double_arcsin_precise', meta_technique='fixed'):
    if meta_technique != 'median':
        filtered_records = get_valid_filtered_records(records, meta_transformation)

        # If there are no remaining records, return None for pooled prevalence estimate
        n_studies = filtered_records.shape[0]
        if n_studies == 0:
            return None

        # Add columns for transformed prevalence and transformed variance based on specified transformation method
        filtered_records['TRANSFORMED_PREVALENCE'] = filtered_records.apply(
            lambda row: calc_transformed_prevalence(row['serum_pos_prevalence'],
                                                    row['denominator_value'],
                                                    meta_transformation),
            axis=1)
        filtered_records['TRANSFORMED_VARIANCE'] = filtered_records.apply(
            lambda row: calc_transformed_variance(row['serum_pos_prevalence'],
                                                  row['denominator_value'],
                                                  meta_transformation),
            axis=1)

        # Calculate the transformed weights and the transformed weighted prevalences only using within study variances
        filtered_records['FIXED_WEIGHT'] = 1 / (filtered_records['TRANSFORMED_VARIANCE'])
        filtered_records['FIXED_WEIGHTED_PREVALENCE'] = filtered_records['TRANSFORMED_PREVALENCE'] * filtered_records[
            'FIXED_WEIGHT']

        fixed_weight_sum = sum(filtered_records['FIXED_WEIGHT'])
        fixed_weighted_prevalence_sum = sum(filtered_records['FIXED_WEIGHTED_PREVALENCE'])
        variance_sum = sum(filtered_records['TRANSFORMED_VARIANCE'])

        # Calculate the transformed pooled prevalence, and the transformed confidence intervals
        trans_pooled_prevalence, trans_conf_inter =\
            get_trans_pooled_prev_and_ci(fixed_weighted_prevalence_sum, fixed_weight_sum, variance_sum)

        # Calculate the sum of all the populations across all studies
        population_sum = sum(filtered_records['denominator_value'])

        # Calculate the overall study population size across all studies using harmonic mean
        average_population_size = hmean(filtered_records['denominator_value'].tolist())

        # If meta analysis technique is fixed effects, back transformed prevalence and error and return body
        if meta_technique == 'fixed':
            pooled_prevalence, error =\
                get_pooled_prevalence_and_error(trans_pooled_prevalence, average_population_size,
                                                meta_transformation, trans_conf_inter)
            return get_return_body(pooled_prevalence, error, population_sum, n_studies, filtered_records['country'])

        # If meta analysis technique is random effects, add between study variance to all calculations
        else:
            # Calculate tau = between study variance
            filtered_records['TRANSFORMED_POOLED_PREVALENCE'] = trans_pooled_prevalence
            tau = calc_between_study_variance(filtered_records)

            # Calculate transformed weights and transformed weighted prevalences also using between study variances
            filtered_records['RANDOM_WEIGHT'] = 1 / (filtered_records['TRANSFORMED_VARIANCE'] + tau)
            filtered_records['RANDOM_WEIGHT_PREVALENCE'] =\
                filtered_records['TRANSFORMED_PREVALENCE'] * filtered_records['RANDOM_WEIGHT']

            random_weight_sum = sum(filtered_records['RANDOM_WEIGHT'])
            random_weighted_prevalence_sum = sum(filtered_records['RANDOM_WEIGHT_PREVALENCE'])
            variance_sum += tau

            # Calculate the transformed pooled prevalence, and the transformed confidence intervals
            trans_pooled_prevalence, trans_conf_inter = \
                get_trans_pooled_prev_and_ci(random_weighted_prevalence_sum, random_weight_sum, variance_sum)

            pooled_prevalence, error = get_pooled_prevalence_and_error(trans_pooled_prevalence, average_population_size,
                                                                       meta_transformation, trans_conf_inter)
            return get_return_body(pooled_prevalence, error, population_sum, n_studies, filtered_records['country'])
    else:
        # Remove records where prevalence is null, or denominator is null or 0
        filtered_records = records[(records['serum_pos_prevalence'].notna()) &
                                   (records['denominator_value'].notna()) &
                                   (records['denominator_value'] > 0)]

        # If there are no remaining records, return None for pooled prevalence estimate
        n_studies = filtered_records.shape[0]
        if n_studies == 0:
            return None

        # Calculate pooled prevalence based on median prevalence
        prevalence_list = filtered_records['serum_pos_prevalence'].tolist()
        median_prevalence = median(prevalence_list)

        # Calculate error based on first and third quartiles
        q1 = quantile(prevalence_list, 0.25)
        q3 = quantile(prevalence_list, 0.75)
        error = [abs(median_prevalence - i) for i in [q1, q3]]
        population_sum = sum(filtered_records['denominator_value'])

        # Get return body and add number of countries if there are multiple countries
        return_body =\
            get_return_body(median_prevalence, error, population_sum, n_studies, filtered_records['country'])
        return return_body


def group_by_agg_var(data, agg_var):
    options = list(data[agg_var].dropna().unique())
    data.dropna(subset=[agg_var], inplace=True)
    return {name: data[data[agg_var].apply(lambda x: name in x)] for name in options}


def get_meta_analysis_records(data, agg_var, transformation, technique):
    data_df = pd.DataFrame(data)
    meta_analysis_records = {}
    if agg_var is not None:
        for name, records in group_by_agg_var(data_df, agg_var).items():
            pooled_prev_results = calc_pooled_prevalence_for_subgroup(records, transformation, technique)
            if pooled_prev_results is not None:
                meta_analysis_records[name] = pooled_prev_results
        return meta_analysis_records
    else:
        return_body = calc_pooled_prevalence_for_subgroup(data_df, transformation, technique)
        return return_body
