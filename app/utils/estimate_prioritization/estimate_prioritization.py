import pandas as pd
from statsmodels.stats.proportion import proportion_confint
from app.utils.estimate_prioritization import prioritization_criteria_testunadj, \
    prioritization_criteria_testadj, pooling_function_maps


def get_pooled_estimate(estimates):

    if estimates.shape[0] == 1:
        pooled = estimates.iloc[0]
    else:
        # use the estimate with the max denominator as the 'base' for the pooled estimate
        pooled = estimates.loc[estimates['denominator_value'].idxmax(axis = 1)] 

        # pool all values that can be pooled
        for (summary_type, cols_to_summarize, summary_function) in pooling_function_maps:
            if summary_function is not None:
                valid_cols_to_summarize = set(cols_to_summarize) & set(estimates.columns)

                for col in valid_cols_to_summarize:
                    pooled.at[col] = summary_function(estimates, col)

        # generate new values as necessary
        pooled.at['numerator_value'] = int(pooled.at['serum_pos_prevalence'] * pooled.at['denominator_value'])
        if 'estimate_name' in pooled.index:
            pooled.at['estimate_name'] += '_pooled'
        pooled.at['seroprev_95_ci_lower'], pooled.at['seroprev_95_ci_upper'] = proportion_confint(count = pooled.at['numerator_value'],
                                                                                          nobs = pooled.at['denominator_value'],
                                                                                          alpha = 0.05,
                                                                                          method = 'jeffreys')
        
        try:
            pooled.at['adj_prev_ci_lower'], pooled.at['adj_prev_ci_upper'] = proportion_confint(count = int(pooled.at['adj_prevalence'] * pooled.at['denominator_value']),
                                                                                                nobs = pooled.at['denominator_value'],
                                                                                                alpha = 0.05,
                                                                                                method = 'jeffreys')
        except KeyError as e: 
            pass

    return pooled

# pass in a filtered set of estimates - or estimates and filters
# and get out a subset, which have an estimate prioritized from among them 
def get_prioritized_estimates(estimates, 
                              filters = None, 
                              mode = 'dashboard',
                              pool = True): 
    
    if estimates.shape[0] == 0:
        return None 
    if filters is not None:
        estimates = estimates[filters]
    
    if mode == 'analysis_static':
        prioritization_criteria = prioritization_criteria_testunadj
    elif mode == 'dashboard':
        prioritization_criteria = prioritization_criteria_testadj
    elif mode == 'analysis_dynamic':
        # variables will be dynamically determined for each estimate
        # based on whether there is an author-adjusted estimate available or not 
        prioritization_criteria = None
    
    selected_estimates = []
    for study_name, study_estimates in estimates.groupby('study_name'):
            
        # if there is only one estimate, use that
        if study_estimates.shape[0] == 1:
            selected_estimates.append(study_estimates.iloc[0])
            continue 

        # if using dynamically determined criteria, decide which prioritization criteria to use
        # prioritize author-adjusted values if there is not enough information for us to adjust 
        # prioritize our own adjusted values otherwise 
        if mode == 'analysis_dynamic':

            try:
                frac_test_info_avail = study_estimates['adj_prevalence'].notna().sum() / study_estimates.shape[0]
            except KeyError as e:
                frac_test_info_avail = 0

            if frac_test_info_avail >= 0.65:
                prioritization_criteria = prioritization_criteria_testunadj
            else:
                prioritization_criteria = prioritization_criteria_testadj

        # now, we will apply prioritization criteria to select estimates
            # if a prioritization criterion would remove all estimates, do not apply it
            # if a prioritization criterion would leave you with one estimate, return that index
            # if a prioritization criterion yields multiple estimates, continue applying criteria 

        # select a criterion
        for criterion_name, criterion in prioritization_criteria.items():
            # go through the levels of that criterion, from highest to lowest
            for level in criterion:
                study_estimates_at_level = study_estimates[study_estimates.apply(level, axis = 1)]

                # if any estimates meet the top level, pass those on; if not, continue
                if study_estimates_at_level.shape[0] > 0:
                    study_estimates = study_estimates_at_level
                    break 

            # if this criterion narrowed it down to just one estimate, break; if not, continue 
            if study_estimates.shape[0] == 1: 
                break
        
        # append the remaining estimate
        if pool:
            selected_estimates.append(get_pooled_estimate(study_estimates))
        else:
            selected_estimates.append(study_estimates)
    
    selected_estimate_df = pd.concat(selected_estimates, axis = 1).T.astype(estimates.dtypes.to_dict())
    return selected_estimate_df
