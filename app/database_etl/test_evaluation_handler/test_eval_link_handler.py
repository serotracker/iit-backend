import pandas as pd

TEST_EVAL_CSV_LOCATION = 'test_evaluation_handler/test_evaluations.csv'


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


def get_eval_UID_and_DOI(row):
    if not row['test_manufacturer'] or not row['isotypes']: return [None]*2
    if row['ind_eval_link'] or row['test_linked_uid']: return [row['test_linked_uid'], row['ind_eval_link']]
    test_name, manufacturers, target_isotypes = row['test_name'], row['test_manufacturer'], row['isotypes']

    # CRITERIA A – test name, manufacturer, and target isotype
    # Get all rows matching test name
    matches = test_eval_df[test_eval_df['TestName'] == test_name]
    if matches.empty: return [None]*2

    if manufacturers[0] == 'Zhejiang Orient Gene (Biotech Co LTD':
        manufacturers = ['Zhejiang Orient Gene (Biotech Co LTD China)']

    temp = pd.DataFrame()
    # Get all rows matching any name in manufacturer list
    for manufacturer in manufacturers:
        if manufacturer in manufacturer_mapping: manufacturer = manufacturer_mapping[manufacturer]
        manu = matches[matches['Manufacturer'].str.contains(f"(?i){manufacturer}")]
        temp = temp.append(manu)

    matches = temp
    # Check that targets are exact match
    for i, ev in matches.iterrows():
        if not set(ev['Target']) == set(target_isotypes):
            matches.drop(i)

    if matches.empty: return [None]*2
    if matches.shape[0] == 1: return [matches.iloc[0]['unique_id'], matches.iloc[0]['DOI']]

    # CRITERIA B – sample specimen type
    specimen_type = row['specimen_type']
    new_matches = matches[matches['IndexSampleType'] == specimen_type]

    if not new_matches.empty:
        matches = new_matches
        if matches.shape[0] == 1: return [matches.iloc[0]['unique_id'], matches.iloc[0]['DOI']]

    # CRITERIA C – prioritized reference specimen type
    rankings = {'Lower respiratory specimen': 1, 'Sputum': 3, 'Bronchial aspirate': 3,
                'Respiratory specimen': 4, 'Upper respiratory specimen': 4, 'Nasal mid-turbinate swabs': 5,
                'Nasopharyngeal swabs': 7, 'Swab': 7, 'Serum': 8, 'Pharyngeal swabs': 10, 'Plasma': 11, 'Oropharyngeal swabs': 12,
                'Whole blood': 13, 'Urine': 14, 'Not available': 20, 'not reported': 20, 'Not reported': 20}

    min_rank, top_matches = 100, pd.DataFrame()
    for i, ev in matches.iterrows():
        if pd.isna(ev['ReferenceSampleType']):
            if top_matches.empty or min_rank == 20:
                min_rank = 20
                top_matches = top_matches.append(ev)
                continue
        reference_specimen_types = ev['ReferenceSampleType'].split('; ')
        for ref in reference_specimen_types:
            rank = rankings[ref]
            if rank > min_rank: continue
            if rank == min_rank: top_matches = top_matches.append(ev)  # Same rank, so append
            else:  # rank < min_rank
                min_rank, top_matches = rank, ev.to_frame().T

    if not top_matches.empty:
        matches = top_matches
        if matches.shape[0] == 1: return [matches.iloc[0]['unique_id'], matches.iloc[0]['DOI']]

    # CRITERIA D – largest sample size
    largest_sample_size, top_match = 0, pd.DataFrame()
    for i, ev in matches.iterrows():
        sample_size = ev['SampleSize']
        if sample_size > largest_sample_size:
            largest_sample_size, top_match = sample_size, ev.to_frame().T

    return [top_match['unique_id'], top_match['DOI']]


def apply_test_eval_links(df):
    df['ind_eval_uid_doi'] = df.apply(lambda row: get_eval_UID_and_DOI(row), axis=1)
    df[['test_linked_uid', 'ind_eval_link']] = pd.DataFrame(df['ind_eval_uid_doi'].to_list(), index=df.index)
    df = df.drop(columns=['ind_eval_uid_doi'])
    return df
