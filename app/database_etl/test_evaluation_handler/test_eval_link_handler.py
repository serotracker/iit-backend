import pandas as pd

TEST_EVAL_CSV_LOCATION = 'add'


def get_isotype_list(isotype_str):
    if pd.isna(isotype_str): return []
    if isotype_str == "Total Ig": return ["IgM", "IgG", "IgA"]
    isotypes = isotype_str.split('; ')
    return set(isotypes)


test_eval_df = pd.read_csv(TEST_EVAL_CSV_LOCATION)
test_eval_df['Target'] = test_eval_df.apply(lambda x: get_isotype_list(x['Target']), axis=1)
manufacturer_mapping = {
    'Vircell Microbiologists': 'Vircell S.L.',
    'SNIBE – Shenzhen New Industries Biomedical Engineering Co.': 'Snibe Co., Ltd',
    'Zhejiang Orient Gene (Biotech Co LTD China)': 'Orient Gene Biotech',
    'VivaCheck Biotech': 'VivaChek',
    'Roche Diagnostics': 'Roche'
}


def apply_link(row):
    if not row['test_manufacturer'] or not row['isotypes']: return None
    if row['ind_eval_link']: return row['ind_eval_link']
    test_name, manufacturers, target_isotypes = row['test_name'], row['test_manufacturer'], row['isotypes']

    # CRITERIA 1 – test name, manufacturer, and target isotype
    # Get all rows matching test name
    matches = test_eval_df[test_eval_df['TestName'] == test_name]
    if matches.empty: return None
    ret = pd.DataFrame()

    if manufacturers[0] == 'Zhejiang Orient Gene (Biotech Co LTD':
        manufacturers = ['Zhejiang Orient Gene (Biotech Co LTD China)']

    # Get all rows matching any name in manufacturer list
    for manufacturer in manufacturers:
        if manufacturer in manufacturer_mapping: manufacturer = manufacturer_mapping[manufacturer]
        df = matches[matches['Manufacturer'].str.contains(f"(?i){manufacturer}")]
        ret = ret.append(df)

    # Check that targets are exact match
    for i, r in ret.iterrows():
        if not set(r['Target']) == set(target_isotypes):
            ret.drop(i)

    if ret.empty: return None

    # CRITERIA 2 – sample specimen type
    # TODO: Match the sample specimen type
    return ret


def apply_test_eval_links(df):
    df['ind_eval_link'] = df.apply(lambda row: apply_link(row), axis=1)  # Currently returns dataframe with one or more tests

    # TODO: implement
    # df['test_linked_uid'] = df.apply(lambda row: func_name(row), axis=1)
    return df
