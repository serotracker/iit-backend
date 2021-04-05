import logging

from sqlalchemy import distinct, func

from app.serotracker_sqlalchemy import db_session, DashboardSource, \
    Country
from app.utils.notifications_sender import send_slack_message
import pandas as pd
from typing import Dict, List, Any


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
            "Blood donors",
            "Household and community samples",
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
        "genpop": [
            'Study examining general population seroprevalence',
            'Study examining special population seroprevalence',
        ]
        "subgroup_var": [
           'Geographical area', 'Health care worker exposure', 'Population',
           'Primary Estimate', 'Comorbidities', 'Sex/Gender',
           'Type of health care worker', 'Age', 'Exposure level',
           'Occupation', 'Time frame', 'Race', 'Health care setting',
           'Analysis', 'Patient group', 'Employment status', 'BMI',
           'Test Used', 'Blood type', 'Medications',
           'Exposure level granular', 'Isotype', 'Asymptomatic',
           'Antibody target', 'Alcohol Intake', 'Household size', 'Symptoms',
           'Non-COVID therapy', 'Dwelling', 'Education', 'Ethnicity',
           'Nationality', 'Income', 'Smoking status', 'Travel',
           'Population size/density ', 'Institution', 'SES',
           'Serostatus timing', 'Vaccination Status', 'Recruitment method'
        ],
        "subgroup_cat": {
            'Various options depending on subgroup var',
            'See Airtable or data dictionary for full list'
        }
    }


def get_all_filter_options() -> Dict[str, Any]:
    with db_session() as session:
        options = get_filter_static_options()

        # Get countries
        query = session.query(distinct(getattr(Country, "country_name")))
        results = [q[0] for q in query if q[0] is not None]
        # sort countries in alpha order
        options["country"] = sorted(results)

        options["max_sampling_end_date"] = session.query(func.max(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["min_sampling_end_date"] = session.query(func.min(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["max_publication_end_date"] = session.query(func.max(DashboardSource.publication_date))[0][0].isoformat()
        options["min_publication_end_date"] = session.query(func.min(DashboardSource.publication_date))[0][0].isoformat()
        options["updated_at"] = session.query(func.max(DashboardSource.publication_date))[0][0].isoformat()

        return options


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
