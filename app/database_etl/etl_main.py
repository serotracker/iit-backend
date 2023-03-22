import os
from datetime import datetime
from time import time
from dotenv import load_dotenv

import pandas as pd
from sqlalchemy import create_engine

from app.serotracker_sqlalchemy import DashboardSourceSchema, ResearchSourceSchema
from app.database_etl.postgres_tables_handler import create_dashboard_source_df, create_bridge_tables, \
    create_multi_select_tables, create_country_df, create_research_source_df, format_dashboard_source, \
    add_mapped_variables, validate_records, load_postgres_tables, drop_table_entries, check_filter_options, \
    validate_pooling_function_columns
from app.database_etl.airtable_records_handler import get_all_records, apply_study_max_estimate_grade, \
    apply_min_risk_of_bias, standardize_airtable_data, ingest_sample_frame_goi_filter_options
from app.database_etl.test_adjustment_handler import add_test_adjustments
from app.database_etl.tableau_data_connector import upload_analyze_csv
from app.database_etl.summary_report_generator import SummaryReport
from app.database_etl.location_utils import compute_pin_info
from app.utils import airtable_fields_config

load_dotenv()

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)

CURR_TIME = datetime.now()


def main():
    # etl_report.__exit__() will run whether or not this block is successfully completed
    # see https://www.geeksforgeeks.org/with-statement-in-python/
    with SummaryReport() as etl_report:
        # Create engine to connect to whiteclaw database
        engine = create_engine('postgresql://{username}:{password}@{host_address}/whiteclaw'.format(
            username=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD'),
            host_address=os.getenv('DATABASE_HOST_ADDRESS')))

        # Get all records with airtable API request and load into dataframe
        print("Get all records with airtable API request and load into dataframe")
        dashboard_cols = airtable_fields_config['dashboard']
        research_cols = airtable_fields_config['research']
        dashboard_cols.update(research_cols)
        json = get_all_records(dashboard_cols)
        etl_report.set_num_airtable_records(len(json))
        airtable_master_data = pd.DataFrame(json)

        # Clean raw airtable records to standardize data formats
        print("Clean raw airtable records to standardize data formats")
        airtable_master_data = standardize_airtable_data(airtable_master_data)

        # Add test adjustment data
        print("Add test adjustment data")
        test_adj_start_time = time()
        airtable_master_data = add_test_adjustments(airtable_master_data)
        test_adj_total_time = round((time() - test_adj_start_time) / (60), 2)
        etl_report.set_test_adjusted_time(test_adj_total_time)

        # Record number of records test adjusted and number of divergent estimates
        print("Record number of records test adjusted and number of divergent estimates")
        test_adjusted_records = airtable_master_data[airtable_master_data['test_adjusted_record'] == True].shape[0]
        etl_report.set_num_test_adjusted_records(test_adjusted_records)
        test_adjusted_record_ids = \
            airtable_master_data[airtable_master_data['test_adjusted_record'] == True]['airtable_record_id'].tolist()
        etl_report.set_test_adjusted_record_ids(test_adjusted_record_ids)
        divergent_estimates = airtable_master_data[(airtable_master_data['test_adjusted_record'] == True)
                                                   & (pd.isna(airtable_master_data['adj_prevalence']))].shape[0]
        etl_report.set_num_divergent_estimates(divergent_estimates)
        airtable_master_data.drop(columns=['test_adjusted_record'], inplace=True)

        # Apply min risk of bias to all study estimates
        print("Apply min risk of bias to all study estimates")
        airtable_master_data = apply_min_risk_of_bias(airtable_master_data)

        # Apply study max estimate grade to all estimates in study
        print("Apply study max estimate grade to all estimates in study")
        airtable_master_data = apply_study_max_estimate_grade(airtable_master_data)

        # Create dashboard source df
        print("Create dashboard source df")
        dashboard_source = create_dashboard_source_df(airtable_master_data, current_time=CURR_TIME)

        # Create country table df
        print("Create country table df")
        country_df = create_country_df(dashboard_source, current_time=CURR_TIME)

        # Add country_id's to dashboard_source df
        print("Add country_id's to dashboard_source df")
        # country_dict maps country_name to country_id
        country_dict = {}
        for index, row in country_df.iterrows():
            country_dict[row['country_name']] = row['country_id']
        dashboard_source['country_id'] = dashboard_source['country'].map(lambda a: country_dict[a])

        # Create dictionary to store multi select tables
        print("Create dictionary to store multi select tables")
        multi_select_tables_dict = create_multi_select_tables(airtable_master_data, current_time=CURR_TIME)

        # Create dictionary to store bridge tables
        print("Create dictionary to store bridge tables")
        bridge_tables_dict = create_bridge_tables(dashboard_source, multi_select_tables_dict, current_time=CURR_TIME)

        # Add mapped variables to master dashboard source table
        print("Add mapped variables to master dashboard source table")
        dashboard_source = add_mapped_variables(dashboard_source)

        # Create research source based on dashboard source
        print("Create research source based on dashboard source")
        research_source, research_source_cols = create_research_source_df(dashboard_source)

        # remove state names from city name column and place them in their own column
        print("remove state names from city name column and place them in their own column")
        multi_select_tables_dict["city"]["state_name"] = multi_select_tables_dict["city"]["city_name"] \
            .map(lambda a: a if pd.isna(a) else (a.split(",")[1] if "," in a else None))
        multi_select_tables_dict["city"]["city_name"] = multi_select_tables_dict["city"]["city_name"] \
            .map(lambda a: a if pd.isna(a) else (a.split(",")[0] if "," in a else a))
        # do the same for the dashboard source column
        # Also standardize so the column type is always a list (None --> empty list)
        dashboard_source["city"] = dashboard_source["city"] \
            .map(lambda cities: [city if pd.isna(city) else city.split(",")[0] for city in cities] if cities else [])
        dashboard_source["state"] = dashboard_source["state"] \
            .map(lambda states: states if states else [])

        # Compute pin information for each record in dashboard source table
        print("Compute pin information for each record in dashboard source table")
        geo_dfs = {
            'city': multi_select_tables_dict['city'],
            'state': multi_select_tables_dict['state'],
            'country': country_df
        }
        dashboard_source = compute_pin_info(dashboard_source, geo_dfs)

        # Format dashboard source table after creating research source
        print("Format dashboard source table after creating research source")
        dashboard_source = format_dashboard_source(dashboard_source, research_source_cols)
        # Validate the dashboard source df

        print("Validate the dashboard source df")
        dashboard_source = validate_records(dashboard_source, DashboardSourceSchema())
        research_source = validate_records(research_source, ResearchSourceSchema())

        # key = table name, value = table df
        tables_dict = {**multi_select_tables_dict,
                       **bridge_tables_dict,
                       'dashboard_source': dashboard_source,
                       'research_source': research_source,
                       'country': country_df}

        # Load dataframes into postgres tables
        print("Load dataframes into postgres tables")
        load_status = load_postgres_tables(tables_dict, engine)

        # If all tables were successfully loaded, drop old entries
        if load_status:
            drop_table_entries(current_time=CURR_TIME, drop_old=True)
            etl_report.set_table_counts_after()
        # Otherwise drop entries from current ETL run
        else:
            drop_table_entries(current_time=CURR_TIME, drop_old=False)

        # Make sure that filter options are still valid
        print("Make sure that filter options are still valid")
        check_filter_options(dashboard_source)

        # Update ordering and translations for filter options
        print("Update ordering and translations for filter options ")
        ingest_sample_frame_goi_filter_options()

        # See if any columns in the db are missing pooling functions
        print("See if any columns in the db are missing pooling functions")
        validate_pooling_function_columns(tables_dict)

        # Upload tableau csv to google sheets with prioritization estimates
        # print("Upload tableau csv to google sheets with prioritization estimates")
        # upload_analyze_csv(canadian_data=False)

        # Upload tableau csv to google sheets without prioritizing estimates for canadian data
        # print("Upload tableau csv to google sheets without prioritizing estimates for canadian data")
        # upload_analyze_csv(canadian_data=True)
        print("DONE RUNNING WOHOOOO!")
        return


if __name__ == '__main__':
    beginning = time()
    main()
    diff = time() - beginning
    print(diff)
