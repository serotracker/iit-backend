import pandas as pd
import datetime
from statsmodels.stats.proportion import proportion_confint
from app.utils.estimate_prioritization_new import prioritization_criteria_testunadj, \
    prioritization_criteria_testadj, pooling_function_maps

'''
# write some code in order to take the union of the colnames
columns_in_database = set() # PLACEHOLDER 
columns_with_pooling_functions = set.union(*[set(pooling_function_map.column_names) 
                                           for pooling_function_map
                                           in pooling_function_maps])
columns_calculated_otherwise = {'seroprev_95_ci_lower',
                                'seroprev_95_ci_upper'
                                'numerator_value',
                                'estimate_name'}
columns_missing_intersection_functions = columns_in_database - columns_with_pooling_functions - columns_calculated_otherwise
if columns_missing_intersection_functions:
    # OUTPUT TO SLACK
    print(f'pooling functions missing for columns {columns_missing_intersection_functions} in file INSERT_FINAL_FILENAME_HERE.py')
'''


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

        # TODO: once test adjustment is in, we'll need to add a parallel set of code to the above
        # for adjusted numerator, denominator, 95% CIs

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
            print(study_estimates['estimate_grade'])
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

if __name__ == '__main__':

    # create minimum set of data needed to test behavior of estimate prioritization code 
    sample_estimates = [
        {
            'IDENTIFIER': 0,
            'study_name': 'Study 1',
            'serum_pos_prevalence': 0.1,
            'denominator_value': 100,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': True,  
            'dashboard_primary_estimate': True, 
            'pop_adj': True,
            'test_adj': True,
        },
        {
            'IDENTIFIER': 1,
            'study_name': 'Study 1',
            'serum_pos_prevalence': 0.2,
            'denominator_value': 200,
            'subgroup_var': 'Test 2',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': None,
        },
        {
            'IDENTIFIER': 2,
            'study_name': 'Study 1',
            'serum_pos_prevalence': 0.3,
            'denominator_value': 300,
            'subgroup_var': 'Test 2',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': None,
            'test_adj': True,
        },
        {
            'IDENTIFIER': 3,
            'study_name': 'Study 1',
            'serum_pos_prevalence': 0.4,
            'denominator_value': 400,
            'subgroup_var': 'Test 2',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': None,
            'test_adj': None,
        },
        {
            'IDENTIFIER': 4,
            'study_name': 'Study 1',
            'serum_pos_prevalence': 0.5,
            'denominator_value': 500,
            'subgroup_var': 'Test 2',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
        },
        {
            'IDENTIFIER': 0,
            'study_name': 'Study 2',
            'serum_pos_prevalence': 0.1,
            'denominator_value': 100,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL'
        },
        {
            'IDENTIFIER': 1,
            'study_name': 'Study 2',
            'serum_pos_prevalence': 0.4,
            'denominator_value': 200,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL'
        },
        {
            'IDENTIFIER': 0,
            'study_name': 'isotype',
            'serum_pos_prevalence': 0.1,
            'denominator_value': 100,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL'
        },
        {
            'IDENTIFIER': 1,
            'study_name': 'isotype',
            'serum_pos_prevalence': 0.4,
            'denominator_value': 200,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL'
        },
        {
            'IDENTIFIER': 0,
            'study_name': 'isotype comb',
            'serum_pos_prevalence': 0.1,
            'denominator_value': 100,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL'
        },
        {
            'IDENTIFIER': 1,
            'study_name': 'isotype comb',
            'serum_pos_prevalence': 0.4,
            'denominator_value': 200,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'AND',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL'
        },
        {
            'IDENTIFIER': 0,
            'study_name': 'test type',
            'serum_pos_prevalence': 0.1,
            'denominator_value': 100,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL'
        },
        {
            'IDENTIFIER': 1,
            'study_name': 'test type',
            'serum_pos_prevalence': 0.4,
            'denominator_value': 200,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'LFIA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL'
        },
        {
            'IDENTIFIER': 0,
            'study_name': 'specimen type',
            'serum_pos_prevalence': 0.1,
            'denominator_value': 100,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL',
            'TEST_INFO_AVAIL': False
        },
        {
            'IDENTIFIER': 1,
            'study_name': 'specimen type',
            'serum_pos_prevalence': 0.4,
            'denominator_value': 200,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Not Dried Blood',
            'age': 'All',
            'sex': 'ALL',
            'TEST_INFO_AVAIL': False
        },
        {
            'IDENTIFIER': 0,
            'study_name': 'dynamic adjustment',
            'serum_pos_prevalence': 0.1,
            'denominator_value': 100,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': True,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Dried Blood',
            'age': 'All',
            'sex': 'ALL',
            'TEST_INFO_AVAIL': False
        },
        {
            'IDENTIFIER': 1,
            'study_name': 'dynamic adjustment',
            'serum_pos_prevalence': 0.4,
            'denominator_value': 200,
            'subgroup_var': 'Primary Estimate',
            'academic_primary_estimate': None,  
            'dashboard_primary_estimate': None, 
            'pop_adj': True,
            'test_adj': False,
            'isotypes_reported': ['IgG', 'IgM'],
            'isotype_comb': 'OR',
            'test_type': 'ELISA',
            'specimen_type': 'Not Dried Blood',
            'age': 'All',
            'sex': 'ALL',
            'TEST_INFO_AVAIL': False
        },
    ]

    # Adding these hardcoded values for now to make tests pass
    for estimate in sample_estimates:
        estimate['population_group'] = "General Population"
        estimate['state'] = ["Texas"]
        estimate['city'] = ["Dallas"]
        estimate['estimate_grade'] = 'National'

    sample_df = pd.DataFrame(sample_estimates)
    # Adding these hardcoded values for now to make tests pass
    sample_df['sampling_start_date'] = datetime.datetime.now()
    sample_df['sampling_end_date'] = datetime.datetime.now()

    # test estimate prioritization code on that minimum set
    def estimate_prioritization_test(estimates,
                                    filters = None,
                                    mode = 'analysis',
                                    test_name = None,
                                    **kwargs #to define arbitrary parameters to check against the result
                                    ):
        result = get_prioritized_estimates(estimates, filters, mode).iloc[0]
        
        print(test_name)
        for var_name, expected in kwargs.items():
            actual = result[var_name]
            match = 'matched' if expected == actual else 'did not match'
            print(f'{var_name} {match}: expected {expected}, got {actual}')
            
        print()        

    estimate_prioritization_test(sample_df, 
                                (sample_df['study_name'] == 'Study 1'),
                                mode = 'analysis_static',
                                test_name = 'PRIMARY ESTIMATE SELECTION',
                                IDENTIFIER = 0)

    estimate_prioritization_test(sample_df, 
                                (sample_df['subgroup_var'] != 'Primary Estimate') & \
                                (sample_df['study_name'] == 'Study 1'), 
                                mode = 'analysis_static',
                                test_name = 'ANALYSIS ADJUSTMENT SELECTION',
                                IDENTIFIER = 1)

    estimate_prioritization_test(sample_df, 
                                (sample_df['subgroup_var'] != 'Primary Estimate') & \
                                (sample_df['study_name'] == 'Study 1'),
                                mode = 'dashboard',
                                test_name = 'DASHBOARD ADJUSTMENT SELECTION',
                                IDENTIFIER = 4)

    estimate_prioritization_test(sample_df, 
                                (sample_df['study_name'] == 'Study 2'),
                                mode = 'analysis_static',
                                IDENTIFIER = 1,
                                denominator_value = 300,
                                test_name = 'POOLING OF IDENTICAL ESTIMATES',
                                serum_pos_prevalence = 0.3)

    estimate_prioritization_test(sample_df, 
                                (sample_df['study_name'] == 'isotype'),
                                mode = 'analysis_static',
                                IDENTIFIER = 0,
                                test_name = 'ISOTYPE')

    estimate_prioritization_test(sample_df, 
                                (sample_df['study_name'] == 'isotype comb'),
                                mode = 'analysis_static',
                                IDENTIFIER = 0,
                                test_name = 'ISOTYPE COMBINATION')

    estimate_prioritization_test(sample_df, 
                                (sample_df['study_name'] == 'test type'),
                                mode = 'analysis_static',
                                IDENTIFIER = 0,
                                test_name = 'TEST TYPE')

    estimate_prioritization_test(sample_df, 
                                (sample_df['study_name'] == 'specimen type'),
                                mode = 'analysis_static',
                                IDENTIFIER = 1,
                                test_name = 'SPECIMEN TYPE')

    estimate_prioritization_test(sample_df, 
                                (sample_df['study_name'] == 'dynamic adjustment'),
                                mode = 'analysis_dynamic',
                                IDENTIFIER = 0,
                                test_name = 'DYNAMIC ADJUSTMENT')
