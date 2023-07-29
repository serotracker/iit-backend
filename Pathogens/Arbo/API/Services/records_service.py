from sqlalchemy import select, distinct
from sqlalchemy.orm import Session

from Pathogens.Arbo.app.sqlalchemy.sql_alchemy_base import Estimate, db_engine


def get_all_arbo_records():
    with Session(db_engine) as session:
        records = session.query(Estimate).all()

        # Convert records to a list of dictionaries
        record_dicts = [record.__dict__ for record in records]

        # Remove unnecessary attributes from the dictionaries
        for record_dict in record_dicts:
            record_dict.pop("_sa_instance_state")

        # Convert the list of dictionaries to JSON
        # Print or do whatever you want with the JSON data
        print(record_dicts)

        return record_dicts


def get_all_arbo_filter_options():
    with Session(db_engine) as session:
        age_group = session.query(distinct(Estimate.age_group)).all()
        sex = session.query(distinct(Estimate.sex)).all()
        assay = session.query(distinct(Estimate.assay)).all()
        country = session.query(distinct(Estimate.country)).all()
        producer = session.query(distinct(Estimate.producer)).all()
        sample_frame = session.query(distinct(Estimate.sample_frame)).all()

        result_dict = {
            "age_group": [item[0] for item in age_group],
            "sex": [item[0] for item in sex],
            "assay": [item[0] for item in assay],
            "country": [item[0] for item in country],
            "producer": [item[0] for item in producer],
            "sample_frame": [item[0] for item in sample_frame]
        }

        return result_dict