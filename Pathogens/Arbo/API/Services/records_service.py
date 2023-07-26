from sqlalchemy import select
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