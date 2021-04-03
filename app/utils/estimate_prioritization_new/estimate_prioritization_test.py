from app.utils.estimate_prioritization_new import get_prioritized_estimates
import datetime
import pandas as pd

# test estimate prioritization code on that minimum set
def estimate_prioritization_test(estimates,
                                filters = None,
                                mode = 'analysis',
                                test_name = None,
                                **kwargs #to define arbitrary parameters to check against the result
                                ):
    result = get_prioritized_estimates(estimates, filters, mode).iloc[0]

    for var_name, expected in kwargs.items():
        actual = result[var_name]
        try:
            assert expected == actual
        except Exception as e:
            print(f"Failed test: {test_name}. Expected {expected}, actual {actual}")
            raise e

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

    print("All tests passed!")