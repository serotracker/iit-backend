from collections import namedtuple
import pandas as pd
from typing import Any

# we will need to 'pool' estimates, collapsing values from multiple estimates to one
# here are functions that do that for each variable
PoolingFnMap = namedtuple(typename = 'PoolingFnMap',
                          field_names = ['summary_type',
                                         'column_names',
                                         'summary_function'])

# helper function to use to generate lambdas
def get_unique_value(series: pd.Series, default: Any = pd.NA) -> Any:
    unique_vals = series.dropna().unique()
    if len(unique_vals) == 1:
        return unique_vals[0]
    else:
        return default

def weighted_average(df: pd.DataFrame, values: str, weights: str) -> float:
    df = df.dropna(axis = 'index', 
                   how = 'any', 
                   subset = [values, weights])
    return ((df[weights] * df[values]).sum() / 
             df[weights].sum())

pooling_function_maps = [
    PoolingFnMap(summary_type = 'sum',
                 column_names = ['denominator_value',
                                 'case_count_0',
                                 'case_count_neg14',
                                 'case_count_neg9',
                                 'case_population',
                                 'death_count_plus11',
                                 'death_count_plus4',
                                 'deaths_population'],
                 summary_function = lambda estimates, col: estimates[col].sum(skipna = True)),
    PoolingFnMap(summary_type = 'union',
                 column_names = ['state',
                                 'city',
                                 'antibody_target',
                                 'test_manufacturer'],
                 # Note need to return standard python list instead of ndarray
                 summary_function = lambda estimates, col: estimates[col].explode().dropna().unique().tolist()),
    PoolingFnMap(summary_type = 'min',
                 column_names = ['sampling_start_date',
                                'age_min'],
                 summary_function = lambda estimates, col: estimates[col].min()),
    PoolingFnMap(summary_type = 'max',
                 column_names = ['sampling_end_date',
                                 'date_created',
                                 'last_modified_time',
                                 'publication_date',
                                 'age_max'],
                 summary_function = lambda estimates, col: estimates[col].max()),
    PoolingFnMap(summary_type = 'mean',
                 column_names = ['pin_latitude',
                                 'pin_longitude'],
                 summary_function = lambda estimates, col: estimates[col].mean()),
    PoolingFnMap(summary_type = 'logical_AND',
                 column_names = ['academic_primary_estimate',
                                 'dashboard_primary_estimate',
                                 'pop_adj',
                                 'test_adj',
                                 'geo_exact_match',
                                 'included',
                                 'include_in_srma'],
                 summary_function = lambda estimates, col: estimates[col].fillna(True).max()),
    PoolingFnMap(summary_type = 'unique_value_or_na',
                 column_names = ['country',
                                 'country_iso3',
                                 'gbd_region',
                                 'gbd_subregion',
                                 'lmic_hic',
                                 'subgroup_var',
                                 'subgroup_cat',
                                 'ind_eval_type'],
                 summary_function = lambda estimates, col: get_unique_value(estimates[col], pd.NA)),
    PoolingFnMap(summary_type = 'unique_value_population_group',
                 column_names = ['population_group'],
                 summary_function = lambda estimates, col: get_unique_value(estimates[col], 'Multiple populations')),
    PoolingFnMap(summary_type = 'unique_value_age',
                 column_names = ['age'],
                 summary_function = lambda estimates, col: get_unique_value(estimates[col], 'Multiple groups')),
    PoolingFnMap(summary_type = 'unique_value_population_group',
                 column_names = ['sex'],
                 summary_function = lambda estimates, col: get_unique_value(estimates[col], 'All')),
    PoolingFnMap(summary_type = 'unique_value_genpop',
                 column_names = ['genpop'],
                 summary_function = lambda estimates, col: get_unique_value(estimates[col], 'Study examining special population seroprevalence')),
    PoolingFnMap(summary_type = 'unique_value_isotype_comb',
                 column_names = ['isotype_comb'],
                 summary_function = lambda estimates, col: get_unique_value(estimates[col], 'AND')),
    PoolingFnMap(summary_type = 'unique_value_specimen_test_type',
                 column_names = ['specimen_type', 'test_type'],
                 summary_function = lambda estimates, col: get_unique_value(estimates[col], 'Multiple Types')),
    PoolingFnMap(summary_type = 'unique_value_test_validation',
                 column_names = ['genpop'],
                 summary_function = lambda estimates, col: get_unique_value(estimates[col], 'Multiple tests with diff validations or values derived from each type')),
    PoolingFnMap(summary_type = 'concatenate_with_semicolons',
                 column_names = ['sample_frame_info',
                                 'test_name',
                                 'subgroup_specific_category'],
                 summary_function = lambda estimates, col: '; '.join(estimates[col].dropna().unique())),
    PoolingFnMap(summary_type = 'identity_from_max_denominator',
                 column_names = ['test_manufacturer',
                                 'sensitivity',
                                 'specificity',
                                 'adj_sensitivity', 
                                 'adj_specificity',
                                 'ind_se',
                                 'ind_sp',
                                 'number_of_females',
                                 'number_of_males',
                                 'ind_se_n',
                                 'ind_sp_n',
                                 'se_n',
                                 'sp_n',
                                 'age_variation',
                                 'average_age',
                                 'ind_eval_lab',
                                 'ind_eval_link',
                                 'test_linked_uid',
                                 'test_not_linked_reason',
                                 'test_validation',
                                 'isotypes_reported',
                                 'url',
                                 'first_author',
                                 'lead_organization',
                                 'source_publisher',
                                 'summary',
                                 'jbi_1', 'jbi_2', 'jbi_3',
                                 'jbi_4', 'jbi_5', 'jbi_6',
                                 'jbi_7', 'jbi_8', 'jbi_9',
                                 'measure_of_age',
                                 'overall_risk_of_bias',
                                 'estimate_grade',
                                 'source_name',
                                 'study_name',
                                 'source_id',
                                 'study_type',
                                 'source_type',
                                 'age_variation_measure',
                                 'sampling_type',
                                 'sampling_method',
                                 'pin_region_type',
                                 'numerator_definition'],
                 summary_function = None),
    PoolingFnMap(summary_type = 'weighted_average_by_denominator',
                 column_names = ['serum_pos_prevalence',
                                 'adj_prevalence',
                                 'cases_per_hundred',
                                 'deaths_per_hundred',
                                 'full_vaccinations_per_hundred',
                                 'vaccinations_per_hundred',
                                 'tests_per_hundred'],
                 summary_function = lambda estimates, col: weighted_average(estimates, col, 'denominator_value')),
]

# Helper function to help with validating that all columns
# in the database are accounted for during the pooling process
# (will be done in the ETL)
def get_columns_with_pooling_functions() -> set:
    columns_with_pooling_functions = set.union(*[set(pooling_function_map.column_names)
                                                 for pooling_function_map
                                                 in pooling_function_maps])
    # account for columns calculated otherwise
    columns_with_pooling_functions = set.union(columns_with_pooling_functions, \
                                     {'seroprev_95_ci_lower',
                                      'seroprev_95_ci_upper',
                                      'adj_prev_ci_lower',
                                      'adj_prev_ci_upper',
                                      'numerator_value',
                                      'estimate_name'})
    return columns_with_pooling_functions
