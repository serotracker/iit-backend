import os
import logging

from app.utils import get_filtered_records, send_slack_message
from app.serotracker_sqlalchemy import dashboard_source_cols

import boto3
import pandas as pd
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()


def upload_s3_file(file_name, bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    try:
        bucket.upload_file(Filename=file_name, Key=file_name)
    except ClientError as e:
        body = f'Error uploading to s3 bucket: {e}'
        logging.error(body)
        send_slack_message(body)
        return
    return


def upload_analyze_csv():
    # Get records
    records = get_filtered_records(research_fields=False, filters=None, columns=None, start_date=None,
                                   end_date=None, prioritize_estimates=True)
    records_df = pd.DataFrame(records)

    # Turn lists into comma sep strings
    cols = ['city', 'state', 'test_manufacturer', 'antibody_target', 'isotypes_reported']
    for col in cols:
        records_df[col] = records_df[col].apply(lambda x: ",".join(x))

    # Create CSV
    filepath = "tableau_analyze_records.csv"
    records_df.to_csv(filepath, index=False)

    # If file exists
    if os.path.isfile(filepath):
        upload_s3_file(filepath, 'tableau-csv-data')
        os.remove(filepath)
        pass
    else:
        # Send error email
        message = "ERROR: Analyze CSV was not created"
        logging.error(message)
        send_slack_message(message)
        return
    return


def get_adj_level(row):
    lvl = 0
    if row['test_adj']:
        lvl += 1
    if row['pop_adj']:
        lvl += 1
    return lvl


def upload_canadian_explore_csv():
    # Get Canadian records
    columns = dashboard_source_cols + \
              ["subgroup_var", "subgroup_specific_category", "pop_adj",
               "test_adj", "isotypes_reported", "pin_latitude", "pin_longitude"]
    columns.remove("isotype_igg")
    columns.remove("isotype_iga")
    columns.remove("isotype_igm")
    filters = {
        "country": ["Canada"]
    }
    records = get_filtered_records(research_fields=True, filters=filters, columns=columns,
                                   start_date=None, end_date=None, prioritize_estimates=False)
    records_df = pd.DataFrame(records)

    # Turn lists into comma sep strings
    records_df['isotypes_reported'] = records_df['isotypes_reported'].apply(lambda x: ",".join(x))

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

    # Create CSV
    filepath = "tableau_canadian_explore_records.csv"
    records_df.to_csv(filepath, index=False)

    # If file exists
    if os.path.isfile(filepath):
        upload_s3_file(filepath, 'tableau-csv-data')
        os.remove(filepath)
        pass
    else:
        # Send error email
        message = "ERROR: Canadian Explore CSV was not created"
        logging.error(message)
        send_slack_message(message)
        return
    return


if __name__ == "__main__":
    upload_analyze_csv()
