import pandas as pd
import numpy as np
from app.utils import get_filtered_records

# Get records
records = get_filtered_records(research_fields=True)
all_estimates = pd.DataFrame(records)

def get_ind_eval_type(estimate):
    # unadjusted estimate available and thus prioritized in estimate selection code
    if estimate['test_adj']:
        # Independent evaluation is available
        if pd.notna(estimate['ind_se']) and pd.notna(estimate['ind_sp']):
            return 'FINDDx / MUHC independent evaluation'
        # Author evaluation is available
        elif pd.notna(estimate['se_n']) and pd.notna(estimate['sp_n']) and \
                pd.notna(estimate['sensitivity']) and pd.notna(estimate['specificity']):
            if estimate['test_validation'] and 'Validated by independent authors/third party/non-developers' in estimate['test_validation']:
                return 'Author-reported independent evaluation'
            else:
                return 'Test developer / manufacturer evaluation'

        elif pd.notna(estimate['sensitivity']) and pd.notna(estimate['specificity']):
            return 'Test developer / manufacturer evaluation'
        else:
            for test_type in ['LFIA', 'CLIA', 'ELISA']:
                if estimate['test_type'] and test_type == estimate['test_type']:
                    return 'Used Bastos SR/MA data; no sens, spec, or author adjustment available'
            return 'No data altogether'
    else:
       return 'Used author-adjusted estimate'

all_estimates['ind_eval_type'] = all_estimates.apply(lambda row: get_ind_eval_type(row), axis=1)

test_set = pd.concat([
    all_estimates[all_estimates["ind_eval_type"] == 'FINDDx / MUHC independent evaluation'][:15],
    all_estimates[all_estimates["ind_eval_type"] == 'Used author-adjusted estimate'][:5]
], ignore_index=True)

# For some reason nulls are being converted to False for these two cols
# although the raw output of "get_filtered_records" gives out nulls as expected
false_cols = ['ind_se', 'ind_sp', 'ind_se_n', 'ind_sp_n', 'se_n', 'sp_n', 'sensitivity',
              'specificity','denominator_value', 'serum_pos_prevalence', 'test_adj']
for col in false_cols:
    test_set[col] = test_set[col].replace(to_replace=False, value=np.nan)

test_set.to_csv("test_adj_test_set.csv")

