import pandas as pd
import numpy as np
from statsmodels.stats.proportion import proportion_confint
from app.utils.estimate_prioritization import prioritization_criteria_testunadj, \
    prioritization_criteria_testadj, pooling_function_maps
from typing import Union


def get_pooled_estimate(estimates: pd.DataFrame) -> pd.DataFrame:
    
    # if only one estimate provided, no pooling necessary - return that estimate 
    if estimates.shape[0] == 1:
        pooled = estimates.iloc[0]
    else:
        # use the estimate with the max denominator to provide series names and default values for the pooled estimate
        # this serves as a "base estimate" that can be subsequently modified 
        pooled = estimates.loc[estimates['denominator_value'].idxmax(axis = 1)] 

        # for each variable that we have a defined pooling function for
        # attempt to generate a pooled value for this variable by applying the pooling function to the input data
        for (_, cols_to_summarize, summary_function) in pooling_function_maps:
            if summary_function is not None:
                # check to ensure that the value to be pooled is in the data input provided 
                valid_cols_to_summarize = set(cols_to_summarize) & set(estimates.columns)

                for col in valid_cols_to_summarize:
                    pooled.at[col] = summary_function(estimates, col)

        # once all pooled variables have been calculated, generate necessary pooled variables based on those calculated variables
        # including numerator, estimate name, and confidence intervals for proportions
        pooled.at['numerator_value'] = int(pooled.at['serum_pos_prevalence'] * pooled.at['denominator_value'])
        if 'estimate_name' in pooled.index:
            pooled.at['estimate_name'] += '_pooled'
        pooled.at['seroprev_95_ci_lower'], pooled.at['seroprev_95_ci_upper'] = proportion_confint(count = pooled.at['numerator_value'],
                                                                                          nobs = pooled.at['denominator_value'],
                                                                                          alpha = 0.05,
                                                                                          method = 'jeffreys')
        
        # try/except ensures that this doesn't break if we are prioritizing estimates from dashboard source only
        # i.e., where pooled.at['adj_prevalence'] will throw a KeyError
        try:
            if pd.notna(pooled.at['adj_prevalence']) and pd.notna(pooled.at['denominator_value']):
                pooled.at['adj_prev_ci_lower'], pooled.at['adj_prev_ci_upper'] = \
                    proportion_confint(count = int(pooled.at['adj_prevalence'] * pooled.at['denominator_value']),
                                    nobs = pooled.at['denominator_value'], alpha = 0.05, method = 'jeffreys')
            else:
                pooled.at['adj_prev_ci_lower'], pooled.at['adj_prev_ci_upper'] = np.nan, np.nan
        except KeyError: 
            pass

    return pooled


def apply_prioritization_criteria(estimates: pd.DataFrame, 
                                  prioritization_criteria: dict) -> list:
     # applies prioritization criteria to select estimates
        # if a prioritization criterion would remove all estimates, do not apply it
        # if a prioritization criterion would leave you with one estimate, return that estimate
        # if a prioritization criterion yields multiple estimates, continue applying criteria 

    # select a criterion
    for _, criterion in prioritization_criteria.items():
        # go through the levels of that criterion, from highest to lowest
        for level in criterion:
            estimates_at_level = estimates[estimates.apply(level, axis = 1)]

            # if any estimates meet that level, pass those on; if not, continue
            if not estimates_at_level.empty:
                estimates = estimates_at_level
                break 

        # if this criterion narrowed it down to just one estimate, break; if not, continue 
        if estimates.shape[0] == 1: 
            break

    return estimates

def percent_adjustable(estimates: pd.DataFrame) -> float:
    # calculate what percentage of estimates in a df of esitmates are adjustable
    n_estimates = estimates.shape[0]
    n_estimates_with_adj = estimates['adj_prevalence'].notna().sum()
    return n_estimates_with_adj / n_estimates

# pass in a filtered set of estimates - or estimates and filters
# and get out a subset, which have an estimate prioritized from among them 
def get_prioritized_estimates(estimates: pd.DataFrame,
                              filters: Union[tuple, None] = None,
                              mode: str = 'dashboard',
                              pool: bool = True) -> pd.DataFrame:
    
    if estimates.empty:
        return pd.DataFrame()
    if filters is not None:
        # Apply filter lambda functions if they're supplied
        for filter in filters:
            estimates = estimates[estimates.apply(filter, axis = 1)]
    
    selected_estimates = []
    for _, study_estimates in estimates.groupby('study_name'):
            
        # if there is only one estimate, use that
        if study_estimates.shape[0] == 1:
            selected_estimates.append(study_estimates.iloc[0])
            continue

        if mode == 'analysis_static':
            study_estimates = apply_prioritization_criteria(study_estimates, prioritization_criteria_testunadj)
        elif mode == 'dashboard':
            study_estimates = apply_prioritization_criteria(study_estimates, prioritization_criteria_testadj)
        elif mode == 'analysis_dynamic':
            serotracker_adjusted = apply_prioritization_criteria(study_estimates, prioritization_criteria_testunadj)
            author_adjusted = apply_prioritization_criteria(study_estimates, prioritization_criteria_testadj)

            # if we were able to successfully adjust the seroprevalence estimates ourselves, use our own
            # else, use the author's 
            if percent_adjustable(serotracker_adjusted) >= percent_adjustable(author_adjusted):
                study_estimates = serotracker_adjusted
            else:
                study_estimates = author_adjusted
        
        # append the remaining estimate
        if pool:
            selected_estimates.append(get_pooled_estimate(study_estimates))
        else:
            selected_estimates.append(study_estimates)

    if pool:
        selected_estimate_df = pd.concat(selected_estimates, axis=1).T.astype(estimates.dtypes.to_dict())
    else:
        selected_estimate_df = pd.concat(selected_estimates)

    return selected_estimate_df


# Gets prioritized estimates without pooling by a specified subgrouping variable
# "subgroup_var" = subgrouping variable to refrain from pooling by
def get_prioritized_estimates_without_pooling(estimates: pd.DataFrame,
                                subgroup_var: str,
                                filters: Union[tuple, None] = None,
                                **kwargs):
    normal_estimates = get_prioritized_estimates(estimates, filters = filters, **kwargs)
    unpooled_filters = set(filters) if filters else set()
    unpooled_filters = tuple(set.union(unpooled_filters,
                                       set([lambda estimate: estimate['subgroup_var'] == subgroup_var])))
    unpooled_estimates = get_prioritized_estimates(estimates, filters = unpooled_filters, pool = False, **kwargs)

    # return union of unpooled_estimates and normal_estimates
    all_estimates = pd.concat([normal_estimates, unpooled_estimates], ignore_index=True).\
        drop_duplicates(subset=['source_id']).reset_index(drop=True)
    return all_estimates