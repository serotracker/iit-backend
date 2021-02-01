from app.utils import get_filtered_records
from app.serotracker_sqlalchemy import dashboard_source_cols
import pandas as pd
import os
import logging

def upload_analyze_csv():
    records = get_filtered_records(research_fields=False, filters=None, columns=None, start_date=None, end_date=None,
                                  prioritize_estimates=True)
    records_df = pd.DataFrame(records)
    # create CSV
    temp_filepath = "analyze_records.csv"
    records_df.to_csv(temp_filepath, index=False)
    # If file exists
    if os.path.isfile(temp_filepath):
        # TODO: upload to S3
        # delete CSV
        #os.remove(temp_filepath)
        pass
    else:
        # Send error email
        logging.error("ERROR: Analyze CSV was not created")
        # TODO: send slack message with error

    return

def get_adj_level(row):
    lvl = 0
    if row['test_adj']:
        lvl += 1
    if row['pop_adj']:
        lvl += 1
    return lvl

def upload_canadian_explore_csv():
    columns = dashboard_source_cols + ["subgroup_var", "subgroup_specific_category", "pop_adj", "test_adj", "estimate_name"]
    filters = {
        "country": ["Canada"]
    }
    records = get_filtered_records(research_fields=True, filters=filters, columns=columns, start_date=None, end_date=None,
                                  prioritize_estimates=False)
    records_df = pd.DataFrame(records)


    # We only want top level estimates and subgeography estimates, so
    # filter out records with subgroup estimates other than
    # "Primary Estimate" and "Geography"
    records_df = records_df[
        (records_df['subgroup_var'] == "Primary Estimate") | (records_df['subgroup_var'] == "Geographical area")]

    # Get the most adjusted estimate for each subgeography
    records_df['adj_level'] = records_df.apply(lambda row: get_adj_level(row), axis=1)
    # note: need to fill None columns with a placeholder so that groupby works
    records_df['subgroup_specific_category'] = records_df['subgroup_specific_category'].fillna("None")
    records_df = records_df.loc[records_df.groupby(['study_name', 'subgroup_specific_category'])['adj_level'].idxmax()]

    # create CSV
    temp_filepath = "canadian_explore_records.csv"
    records_df.to_csv(temp_filepath, index=False)
    # If file exists
    if os.path.isfile(temp_filepath):
        # TODO: upload to S3
        # delete CSV
        #os.remove(temp_filepath)
        pass
    else:
        # Send error email
        logging.error("ERROR: Canadian Explore CSV was not created")
        # TODO: send slack message with error

    return

if __name__ == "__main__":
    upload_canadian_explore_csv()