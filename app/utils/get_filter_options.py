from app.serotracker_sqlalchemy import db_session, DashboardSource, \
    Country
from sqlalchemy import distinct, func


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
        ]
    }


def get_all_filter_options():
    with db_session() as session:
        options = get_filter_static_options()

        # Get countries
        query = session.query(distinct(getattr(Country, "country_name")))
        results = [q[0] for q in query if q[0] is not None]
        options["country"] = results

        options["max_date"] = session.query(func.max(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["min_date"] = session.query(func.min(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["updated_at"] = session.query(func.max(DashboardSource.publication_date))[0][0].isoformat()

        return options
