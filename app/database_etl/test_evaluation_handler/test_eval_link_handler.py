import pandas as pd

TEST_EVAL_CSV_LOCATION = 'add'


def get_isotype_list(isotype_str):
    if pd.isna(isotype_str): return []
    if isotype_str == "Total Ig": return ["IgM", "IgG", "IgA"]
    isotypes = isotype_str.split('; ')
    return set(isotypes)


test_eval_df = pd.read_csv(TEST_EVAL_CSV_LOCATION)
test_eval_df['Target'] = test_eval_df.apply(lambda x: get_isotype_list(x['Target']), axis=1)


def apply_link(row):
    if row['ind_eval_link'] or not row['test_manufacturer'] or not row['isotypes']: return None
    test_name, manufacturer_name, target_isotypes = row['test_name'], set(row['test_manufacturer']), set(row['isotypes'])

    matches = test_eval_df[test_eval_df['TestName'] == test_name]
    if matches.empty(): return None
    matches = matches[set(matches['Manufacturer']) == manufacturer_name]
    if matches.empty(): return None
    matches = matches[set(matches['Target']) == manufacturer_name]
    return matches


def apply_test_eval_links(df):
    df['ind_eval_link'] = df.apply(lambda row: apply_link(row), axis=1)
    return df
