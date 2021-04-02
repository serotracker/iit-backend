import pandas as pd

# define a full set of prioritization criteria
prioritization_criteria_full = {
    'primary_estimate_testadj': [
        lambda estimate: estimate['dashboard_primary_estimate'] is True
    ],
    'adjustment_testadj': [
        lambda estimate: (estimate['pop_adj'] is True) and (estimate['test_adj'] is True),
        lambda estimate: (pd.isna(estimate['pop_adj'])) and (estimate['test_adj'] is True),
        lambda estimate: (estimate['pop_adj'] is True) and (pd.isna(estimate['test_adj'])),
        lambda estimate: (pd.isna(estimate['pop_adj'])) and (pd.isna(estimate['test_adj'])),
    ],
    'primary_estimate_testunadj': [
        lambda estimate: estimate['academic_primary_estimate'] is True
    ],
    'adjustment_testunadj': [
        lambda estimate: (estimate['pop_adj'] is True) and (pd.isna(estimate['test_adj'])),
        lambda estimate: (pd.isna(estimate['pop_adj'])) and (pd.isna(estimate['test_adj'])),
        lambda estimate: (estimate['pop_adj'] is True) and (estimate['test_adj'] is True),
        lambda estimate: (pd.isna(estimate['pop_adj'])) and (estimate['test_adj'] is True),
    ],
    'estimate_grade': [
        lambda estimate: estimate['estimate_grade'] == 'National',
        lambda estimate: estimate['estimate_grade'] == 'Regional',
        lambda estimate: estimate['estimate_grade'] == 'Local',
        lambda estimate: estimate['estimate_grade'] == 'Sublocal',
    ],
    'age': [
        lambda estimate: estimate['age'] == 'Multiple groups'
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
    'test_type': [
        lambda estimate: estimate['test_type'] == 'Neutralization',
        lambda estimate: estimate['test_type'] == 'CLIA',
        lambda estimate: estimate['test_type'] == 'ELISA'
    ],
    'specimen': [
        lambda estimate: 'Dried Blood' not in estimate['specimen_type']
    ]
}

prioritization_criteria_testadj = {name: criterion for name, criterion
                                  in prioritization_criteria_full.items()
                                  if name.find('testunadj') == -1}

prioritization_criteria_testunadj = {name: criterion for name, criterion
                                    in prioritization_criteria_full.items()
                                    if name.find('testadj') == -1}