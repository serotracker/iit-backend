from app.serotracker_sqlalchemy import db_session, DashboardSource, \
    Country
from sqlalchemy import distinct, func


def get_all_filter_options():
    with db_session() as session:
        # List of fields in DashboardSource to query
        airtable_field_strings = ['source_type', 'overall_risk_of_bias', 'sex', 'estimate_grade',
                                  'population_group', 'age', 'specimen_type', 'test_type']
        options = {}
        for field_string in airtable_field_strings:
            query = session.query(distinct(getattr(DashboardSource, field_string)))
            results = [q[0] for q in query if q[0] is not None]
            options[field_string] = results

        other_fields = {
            "country_name": {
                "table": Country,
                "label": "country"
            }
        }

        for field in other_fields:
            query = session.query(distinct(getattr(other_fields[field]["table"], field)))
            results = [q[0] for q in query if q[0] is not None]
            options[other_fields[field]["label"]] = results

        options["max_date"] = session.query(func.max(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["min_date"] = session.query(func.min(DashboardSource.sampling_end_date))[0][0].isoformat()
        options["updated_at"] = session.query(func.max(DashboardSource.publication_date))[0][0].isoformat()

        return options
