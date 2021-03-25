import os
from datetime import datetime
from time import time
from dotenv import load_dotenv

import pandas as pd
from sqlalchemy import create_engine
from app.serotracker_sqlalchemy import DashboardSourceSchema, ResearchSourceSchema
from app.database_etl.postgres_tables_handler import create_dashboard_source_df, create_bridge_tables,\
    create_multi_select_tables, create_country_df, create_research_source_df, format_dashboard_source,\
    add_mapped_variables, validate_records, load_postgres_tables, drop_table_entries, check_filter_options
from app.database_etl.airtable_records_handler import get_all_records, apply_study_max_estimate_grade,\
    apply_min_risk_of_bias, standardize_airtable_data
from app.database_etl.tableau_data_connector import upload_analyze_csv
from app.database_etl.summary_report_generator import SummaryReport


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
        json = get_all_records()
        etl_report.set_num_airtable_records(len(json))
        data = pd.DataFrame(json)

        # Clean raw airtable records to standardize data formats
        data = standardize_airtable_data(data)

        # Apply min risk of bias to all study estimates
        data = apply_min_risk_of_bias(data)

        # Apply study max estimate grade to all estimates in study
        data = apply_study_max_estimate_grade(data)

        # Create dashboard source df
        dashboard_source = create_dashboard_source_df(data, current_time=CURR_TIME)

        # Create country table df
        country_df = create_country_df(dashboard_source, current_time=CURR_TIME)

        # Add country_id's to dashboard_source df
        # country_dict maps country_name to country_id
        country_dict = {}
        for index, row in country_df.iterrows():
            country_dict[row['country_name']] = row['country_id']
        dashboard_source['country_id'] = dashboard_source['country'].map(lambda a: country_dict[a])

        # Create dictionary to store multi select tables
        multi_select_tables_dict = create_multi_select_tables(data, current_time=CURR_TIME)

        # Create dictionary to store bridge tables
        bridge_tables_dict = create_bridge_tables(dashboard_source, multi_select_tables_dict, current_time=CURR_TIME)

        # Add mapped variables to master dashboard source table
        dashboard_source = add_mapped_variables(dashboard_source)

        # Create research source based on dashboard source
        research_source, research_source_cols = create_research_source_df(dashboard_source)

        # Format dashboard source table after creating research source
        dashboard_source = format_dashboard_source(dashboard_source, research_source_cols)

        # remove state names from city_name field
        multi_select_tables_dict["city"]["city_name"] = multi_select_tables_dict["city"]["city_name"] \
            .map(lambda a: a.split(",")[0] if "," in a else a)

        # Validate the dashboard source df
        dashboard_source = validate_records(dashboard_source, DashboardSourceSchema())
        research_source = validate_records(research_source, ResearchSourceSchema())

        # key = table name, value = table df
        tables_dict = {**multi_select_tables_dict,
                       **bridge_tables_dict,
                       'dashboard_source': dashboard_source,
                       'research_source': research_source,
                       'country': country_df}

        # Load dataframes into postgres tables
        load_status = load_postgres_tables(tables_dict, engine)

        # If all tables were successfully loaded, drop old entries
        if load_status:
            drop_table_entries(current_time=CURR_TIME, drop_old=True)
            etl_report.set_table_counts_after()
        # Otherwise drop entries from current ETL run
        else:
            drop_table_entries(current_time=CURR_TIME, drop_old=False)

        # Make sure that filter options are still valid
        check_filter_options(dashboard_source)

        # Upload tableau csv to google sheets
        upload_analyze_csv()
        return


if __name__ == '__main__':
    beginning = time()
    main()
    diff = time() - beginning
    print(diff)
