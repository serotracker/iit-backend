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

def upload_canadian_explore_csv():
    columns = dashboard_source_cols + ["subgroup_var", "estimate_name"]
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

    # Any records whose estimate name is suffixed with "unadj"
    # Will have an adjusted version at the same geography level
    # Thus we should get rid of any estimates whose names contain "unadj"
    records_df = records_df[~records_df["estimate_name"].str.contains("unadj", case=False)]

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