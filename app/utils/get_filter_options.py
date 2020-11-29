from app.serotracker_sqlalchemy import db_session, AirtableSource, \
    Country
from sqlalchemy import distinct, func


def get_all_filter_options():
    with db_session() as session:
        # List of fields in AirtableSource to query
        airtable_field_strings = ['source_type', 'study_status', 'overall_risk_of_bias', 'sex', 'estimate_grade']
        options = {}
        for field_string in airtable_field_strings:
            query = session.query(distinct(getattr(AirtableSource, field_string)))
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

        options["max_date"] = session.query(func.max(AirtableSource.sampling_end_date))[0]
        options["min_date"] = session.query(func.min(AirtableSource.sampling_end_date))[0]

        return options
