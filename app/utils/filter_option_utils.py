import logging

from sqlalchemy import distinct, func

from app.serotracker_sqlalchemy import db_session, DashboardSource, \
    Country
from app.utils.notifications_sender import send_slack_message

static_filter_options = {
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
        "Students",
        "Contacts of COVID patients",
        "Non-essential workers and unemployed persons",
        "Essential non-healthcare workers",
        "Hospital visitors",
        "Persons who are incarcerated",
        "Persons living in slums",
        "Pregnant or parturient women",
        "Patients seeking care for non-COVID-19 reasons",
        "Household and community samples",
        "Health care workers and caregivers",
    ],
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
    "gbd_region": [
        'Central Europe, Eastern Europe, and Central Asia',
        'High-income',
        'Latin America and Caribbean',
        'North Africa and Middle East',
        'South Asia',
        'Southeast Asia, East Asia, and Oceania',
        'Sub-Saharan Africa'
    ]
}
def get_filter_static_options():
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
            "Students",
            "Contacts of COVID patients",
            "Non-essential workers and unemployed persons",
            "Essential non-healthcare workers",
            "Hospital visitors",
            "Persons who are incarcerated",
            "Persons living in slums",
            "Pregnant or parturient women",
            "Patients seeking care for non-COVID-19 reasons",
            "Household and community samples",
            "Health care workers and caregivers",
        ],
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
        "gbd_region": [
            'Central Europe, Eastern Europe, and Central Asia',
            'High-income',
            'Latin America and Caribbean',
            'North Africa and Middle East',
            'South Asia',
            'Southeast Asia, East Asia, and Oceania',
            'Sub-Saharan Africa'
        ]
    }

all_filter_types = list(get_filter_static_options().keys()) + ['country', 'isotypes_reported']

def get_all_filter_options():
    with db_session() as session:
        options = get_filter_static_options()

        # Get countries
        query = session.query(distinct(getattr(Country, "country_name")))
        results = [q[0] for q in query if q[0] is not None]
        # sort countries in alpha order
        options["country"] = sorted(results)

        options["max_date"] = session.query(func.max(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["min_date"] = session.query(func.min(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["updated_at"] = session.query(func.max(DashboardSource.publication_date))[0][0].isoformat()

        return options


# Send alert email if filter options have changed
def check_filter_options(dashboard_source):
    curr_filter_options = get_filter_static_options()
    to_ignore = set(["All", "Multiple groups", "Multiple populations", "Multiple Types", None])
    changed_filter_options = {}

    for filter_type in curr_filter_options:
        # Get new options for each filter type
        new_options = set(dashboard_source[filter_type].unique())
        # Remove options that are unused (e.g. "All", "Multiple groups", etc)
        new_options = set([s for s in new_options if s not in to_ignore])
        # Check to see if the new options are equal to the curr hardcoded options
        # Check to see if the new options are equal to the curr hardcoded options
        if new_options != set(curr_filter_options[filter_type]):
            changed_filter_options[filter_type] = new_options
            logging.info(new_options)
    if len(changed_filter_options.keys()) > 0:
        body = f"New filter options found in ETL: {changed_filter_options}"
        send_slack_message(message=body, channel='#dev-logging-etl')
