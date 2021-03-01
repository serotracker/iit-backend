import numpy as np

from ..location_utils import get_city


def get_most_recent_publication_info(row):
    # Get index of most recent pub date if the pub date is not None
    try:
        pub_dates = row['publication_date']
        max_index = pub_dates.index(max(pub_dates))
        row['publication_date'] = row['publication_date'][max_index]

    # If pub date is None set to index to 0
    except AttributeError:
        max_index = 0
    # If source type exists, get element at that index
    if row['source_type']:
        # We should take either the max_index based on the latest pub date,
        # or the last element of source type if the max index doesn't exist
        i = min(max_index, len(row['source_type']) - 1)
        row['source_type'] = row['source_type'][i]

    # Index whether org author exists and corresponding first author
    if row['organizational_author'] and row['first_author']:
        # We should take either the max_index based on the latest pub date,
        # or the last element of org author if the max index doesn't exist
        i = min(max_index, len(row['organizational_author']) - 1)
        is_org_author = row['organizational_author'][i]
        row['organizational_author'] = is_org_author

        # We should take either the max_index based on the latest pub date,
        # or the last element of first author if the max index doesn't exist
        i = min(max_index, len(row['first_author']) - 1)
        row['first_author'] = row['first_author'][i]

        # If it is not an organizational author, then get last name
        if not is_org_author and len(row['first_author']) > 0:
            row['first_author'] = row['first_author'].strip().split()[-1]
    return row


def standardize_airtable_data(df):
    # List of columns that are lookup fields and therefore only have one element in the list
    single_element_list_cols = ['included', 'source_name', 'url', 'source_publisher', 'summary',
                                'study_type', 'country', 'lead_organization', 'overall_risk_of_bias',
                                'age_variation', 'age_variation_measure', 'ind_eval_lab', 'ind_eval_link',
                                'ind_se', 'ind_se_n', 'ind_sp', 'ind_sp_n', 'jbi_1', 'jbi_2', 'jbi_3', 'jbi_4',
                                'jbi_5', 'jbi_6', 'jbi_7', 'jbi_8', 'jbi_9', 'measure_of_age', 'number_of_females',
                                'number_of_males', 'superceded', 'test_linked_uid', 'average_age',
                                'test_not_linked_reason']

    # Remove lists from single select columns
    for col in single_element_list_cols:
        df[col] = df[col].apply(lambda x: x[0] if x is not None else x)

    # Convert elements that are "Not reported" or "Not Reported" or "NR" to None
    df.replace({'nr': None, 'NR': None, 'Not Reported': None, 'Not reported': None, 'Not available': None},
                 inplace=True)

    # Replace columns that should be floats with NaN from None and rescale to percentage
    df[['ind_sp_n', 'ind_se_n']] = df[['ind_sp_n', 'ind_se_n']].replace({None: np.nan}) / 100

    # Drop rows if columns are null: included?, serum pos prevalence, denominator, sampling end
    df.dropna(subset=['included', 'serum_pos_prevalence', 'denominator_value', 'sampling_end_date'],
                inplace=True)

    # Convert superceded to True/False values
    df['superceded'] = df['superceded'].apply(lambda x: True if x else False)

    # Get index of most recent publication date
    df = df.apply(lambda row: get_most_recent_publication_info(row), axis=1)

    # df state, city and test_manufacturer fields to lists
    df['test_manufacturer'] = df['test_manufacturer'].apply(lambda x: x.split(',') if x else x)
    df['state'] = df['state'].apply(lambda x: x.split(',') if x else x)
    df['city'] = df.apply(lambda row: get_city(row), axis=1)
    return df


def apply_min_risk_of_bias(df):
    bias_hierarchy = ['Low', 'Moderate', 'High', 'Unclear']
    for name, subset in df.groupby('study_name'):
        if (subset['overall_risk_of_bias']).isnull().all():
            subset['overall_risk_of_bias'] = 'Unclear'
            continue
        for level in bias_hierarchy:
            if (subset['overall_risk_of_bias'] == level).any() or level == 'Unclear':
                subset['overall_risk_of_bias'] = level
                continue
    return df


def apply_study_max_estimate_grade(df):
    grade_hierarchy = ['National', 'Regional', 'Local', 'Sublocal']
    for name, subset in df.groupby('study_name'):
        for level in grade_hierarchy:
            if (subset['estimate_grade'] == level).any():
                subset['estimate_grade'] = level
                continue
    return df

