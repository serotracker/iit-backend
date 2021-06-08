import logging

from app.utils.notifications_sender import send_slack_message
from app.utils.estimate_prioritization import get_columns_with_pooling_functions
import pandas as pd
from typing import Dict, List


def get_filter_static_options() -> Dict[str, List[str]]:
    return {
        "age": [
            "Adults (18-64 years)",
            "Children and Youth (0-17 years)",
            "Seniors (65+ years)"
        ],
        "estimate_grade": [
            "National",
            "Regional",
            "Local",
            "Sublocal"
        ],
        "overall_risk_of_bias": [
            "Low",
            "Moderate",
            "High",
            "Unclear"
        ],
        "population_group": [
            "Household and community samples",
            "Blood donors",
            "Residual sera",
            "Assisted living and long-term care facilities",
            "Students and Daycares",
            "Contacts of COVID patients",
            "Non-essential workers and unemployed persons",
            "Essential non-healthcare workers",
            "Hospital visitors",
            "Persons who are incarcerated",
            "Persons living in slums",
            "Pregnant or parturient women",
            "Perinatal",
            "Patients seeking care for non-COVID-19 reasons",
            "Household and community samples",
            "Health care workers and caregivers",
            "Family of essential workers"
        ],
        "prioritize_estimates_mode": [
            "analysis_dynamic",
            "analysis_static",
            "dashboard"],
        "sex": [
            "Female",
            "Male",
            "Other"
        ],
        "source_type": [
            "Journal Article (Peer-Reviewed)",
            "Preprint",
            "Institutional Report",
            "News and Media"
        ],
        "specimen_type": [
            "Whole Blood",
            "Dried Blood",
            "Plasma",
            "Serum",
        ],
        "test_type": [
            "Neutralization",
            "CLIA",
            "ELISA",
            "LFIA",
            "Other"
        ],
    }


# Send alert email if filter options have changed
# Typing a function with void return: https://stackoverflow.com/questions/36797282/python-void-return-type-annotation
def check_filter_options(dashboard_source: pd.DataFrame) -> None:
    curr_filter_options = get_filter_static_options()
    to_ignore = set(["All", "Multiple groups", "Multiple populations", "Multiple Types", None])
    changed_filter_options = {}

    for filter_type in curr_filter_options:
        # Skip over prioritize_estimates_mode because it is hard-coded and not in the database
        if filter_type == 'prioritize_estimates_mode': continue
        
        # Get new options for each filter type
        new_options = set(dashboard_source[filter_type].unique())
        # Remove options that are unused (e.g. "All", "Multiple groups", etc)
        new_options = set([s for s in new_options if s not in to_ignore])
        # Check to see if the new options are equal to the curr hardcoded options
        old_options = set(curr_filter_options[filter_type])
        if new_options != old_options:
            options_added = new_options - old_options
            options_removed = old_options - new_options
            changed_filter_options[filter_type] = {}
            changed_filter_options[filter_type]['options_added'] = options_added
            changed_filter_options[filter_type]['options_removed'] = options_removed
            logging.info(new_options)
    if len(changed_filter_options.keys()) > 0:
        body = f"New filter options found in ETL: {changed_filter_options}"
        send_slack_message(message=body, channel='#dev-logging-etl')

    return


# Send slack alert if there are any columns that are not accounted for
# during the pooling process (in estimate prioritization)
def validate_pooling_function_columns(tables_dict: Dict) -> None:
    columns_with_pooling_functions = get_columns_with_pooling_functions()
    # Documentation for set.union() https://www.w3schools.com/python/ref_set_union.asp
    # Note that * in this case means unpacking a list
    columns_in_db = set.union(*[set(table.columns) for table in tables_dict.values()])
    # remove row uuid's and created at timestamps from consideration
    # as they don't need to be accounted for during pooling
    columns_in_db = columns_in_db - {"id", "country_id", "city_id", "state_id", "airtable_record_id",
                                     "test_manufacturer_id", "antibody_target_id", "created_at"}
    # replace columns that will be transformed before getting to estimate prioritization
    columns_in_db = columns_in_db - {"isotype_iga", "isotype_igm", "isotype_igg", "longitude", "latitude", "city_name",
                                     "antibody_target_name", "state_name", "country_name", "test_manufacturer_name"}
    columns_in_db = set.union(columns_in_db, {"pin_latitude", "pin_longitude", "city", "state", "antibody_target",
                                              "country", "test_manufacturer", "isotypes_reported", "pin_region_type"})

    missing_in_pooling = columns_in_db - columns_with_pooling_functions
    missing_in_db = columns_with_pooling_functions - columns_in_db

    if missing_in_pooling:
        msg = f"The following columns are in the DB, but are missing pooling functions: {missing_in_pooling}"
        send_slack_message(message=msg, channel='#dev-logging-etl')
    if missing_in_db:
        msg = f"The following columns have pooling functions, but are missing in the DB: {missing_in_db}"
        send_slack_message(message=msg, channel='#dev-logging-etl')

    return