import pandas as pd
import datetime

# define a full set of prioritization criteria 
prioritization_criteria_full = {
    'adjustment_testadj': [
        lambda estimate: (estimate['pop_adj'] == True) and (estimate['test_adj'] == True),
        lambda estimate: (pd.isna(estimate['pop_adj'])) and (estimate['test_adj'] == True),
        lambda estimate: (estimate['pop_adj'] == True) and (pd.isna(estimate['test_adj'])),
        lambda estimate: (pd.isna(estimate['pop_adj'])) and (pd.isna(estimate['test_adj'])),
    ],
    'adjustment_testunadj': [
        lambda estimate: (estimate['pop_adj'] == True) and (pd.isna(estimate['test_adj'])),
        lambda estimate: (pd.isna(estimate['pop_adj'])) and (pd.isna(estimate['test_adj'])),
        lambda estimate: (estimate['pop_adj'] == True) and (estimate['test_adj'] == True),
        lambda estimate: (pd.isna(estimate['ƒpop_adj'])) and (estimate['test_adj'] == True),
    ],
    'age': [
        lambda estimate: 'All' in estimate['age']
    ],
    'sex': [
        lambda estimate: estimate['sex'] == 'All'
    ],
    'isotype': [
        lambda estimate: 'Total Antibody' in estimate['isotypes_reported'], # total Ab
        lambda estimate: ((len(estimate['isotypes_reported']) > 1) and \
                         ('IgG' in estimate['isotypes_reported']) and \
                         ((estimate['isotype_comb'] == 'OR') or \
                         estimate['isotype_comb'] == 'AND/OR')),   # IgG OR other Ab
        lambda estimate: ((len(estimate['isotypes_reported']) == 1) and \
                         ('IgG' in estimate['isotypes_reported'])),         # IgG alone
        lambda estimate: ((len(estimate['isotypes_reported']) > 1) and \
                         ('IgM' in estimate['isotypes_reported']) and \
                         ((estimate['isotype_comb'] == 'OR') or \
                         estimate['isotype_comb'] == 'AND/OR')),   # IgM OR other Ab
        lambda estimate: ((len(estimate['isotypes_reported']) > 1) and \
                         ('IgG' in estimate['isotypes_reported'])),         # IgG AND other Ab
        lambda estimate: ((len(estimate['isotypes_reported']) == 1) and \
                         ('IgM' in estimate['isotypes_reported'])),         # IgM alone
        lambda estimate: ((len(estimate['isotypes_reported']) > 1) and \
                         ('IgG' in estimate['isotypes_reported']))          # IgM AND other Ab
    ],
    # TODO: reconsider once data clean is in
    # 'assay': [
    #     lambda estimate: 'ELISA' in estimate['test_types_grouped']
    # ],
    'specimen': [
        lambda estimate: 'Dried Blood' is not estimate['specimen_type']
    ],

}

prioritization_criteria_testadj = {name: criterion for name, criterion \
                                  in prioritization_criteria_full.items() \
                                  if name.find('testunadj') == -1}

prioritization_criteria_testunadj = {name: criterion for name, criterion \
                                    in prioritization_criteria_full.items() \
                                    if name.find('testadj') == -1}

# pass in a filtered set of estimates - or estimates and filters
# and get out a subset, which have an estimate prioritized from among them 

def get_pooled_estimate(estimates):
    
    if estimates.shape[0] == 1:
        
        return estimates.iloc[0]
    
    elif estimates.shape[0] > 1:
        
        pooled = estimates.loc[estimates['denominator_value'].idxmax(axis = 1)] # estimate with max denominator
        
        pooled.at['denominator_value'] = sum(estimates['denominator_value'])
        pooled.at['numerator_value'] = sum(estimates['denominator_value'] * estimates['serum_pos_prevalence'])
        
        # have population group, state, and city to be the union of the inputs
        pooled.at['population_group'] = list(estimates['population_group'].explode().dropna().unique())
        pooled.at['state'] = list(estimates['state'].explode().dropna().unique())
        pooled.at['city'] = list(estimates['city'].explode().dropna().unique())
        
        # TODO: include after data clean
        # fix population: general population only if all are genpop, specpop otherwise
        # if (estimates['GENPOP'] == 'Study examining general population seroprevalence').all():
        #     pooled.at['GENPOP'] = 'Study examining general population seroprevalence'
        # else:
        #     pooled.at['GENPOP'] = 'Study examining special population seroprevalence'
        # same pop only if all are the same, multiple otherwise
        # if (estimates['POPULATION'] == estimates['POPULATION'].iloc[0]).all(): # all pops are the same
        #     pooled.at['POPULATION'] = estimates['POPULATION'].iloc[0]
        # else:
        #     pooled.at['POPULATION'] = 'Multiple populations'
        
        # take the minimum sampling start date and the maximum sampling end date
        # Note: dashboard will supply dates as datetimes instead of as strings in the
        # form "YY-MM-DD", something to note for research compatibility
        pooled.at['sampling_start_date'] = estimates['sampling_start_date'].min()
        pooled.at['sampling_end_date'] = estimates['sampling_end_date'].max()

        return pooled  


def get_prioritized_estimates(estimates, 
                              filters = None, 
                              mode = 'analysis_dynamic'): 
    
    if filters is not None:
        estimates = estimates[filters]
    if estimates.shape[0] == 0:
        return None 
    
    if mode == 'analysis_dynamic':
        prioritization_criteria = None
        primary_estimate_var = 'academic_primary_estimate'
    elif mode == 'analysis_static':
        prioritization_criteria = prioritization_criteria_testunadj
        primary_estimate_var = 'academic_primary_estimate'
    else:
        prioritization_criteria = prioritization_criteria_testadj
        primary_estimate_var = 'dashboard_primary_estimate'
    
    selected_estimates = []
    for study_name, study_estimates in estimates.groupby('study_name'):
            
        # if there is only one estimate, use that
        if study_estimates.shape[0] == 1:
            selected_estimates.append(study_estimates.iloc[0])
            continue 

        # else, if using dynamically determined criteria, decide which to use
        if mode == 'analysis_dynamic':

            try:
                frac_test_info_avail = study_estimates['TEST_INFO_AVAIL'].value_counts(normalize = True).loc[True]
            except KeyError as e:
                frac_test_info_avail = 0

            if frac_test_info_avail >= 0.5:
                prioritization_criteria = prioritization_criteria_testunadj
                primary_estimate_var = 'academic_primary_estimate'
            else:
                prioritization_criteria = prioritization_criteria_testadj
                primary_estimate_var = 'dashboard_primary_estimate'

        primary_estimates = study_estimates[study_estimates[primary_estimate_var] == True]

        # if there are any primary estimates, use those
        if primary_estimates.shape[0] >= 1:
            selected_estimates.append(get_pooled_estimate(primary_estimates))
            continue 

        # because we have reached this point, we know that there are no primary estimates - 
        # but there is more than one estimate from this study which meets inclusion criteria 

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
        selected_estimates.append(get_pooled_estimate(study_estimates))
    
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['LFIA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
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
            'test_type': ['ELISA'], 
            'specimen_type': 'Dried Blood',
            'age': ['All'],
            'sex': 'ALL',
            'TEST_INFO_AVAIL': False
        },
    ]

    # Adding these hardcoded values for now to make tests pass
    for estimate in sample_estimates:
        estimate['population_group'] = ["General Population"]
        estimate['state'] = ["Texas"]
        estimate['city'] = ["Dallas"]

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