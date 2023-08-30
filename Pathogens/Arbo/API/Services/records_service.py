from sqlalchemy import select, distinct, func
from sqlalchemy.orm import Session

from Pathogens.Arbo.app.sqlalchemy.sql_alchemy_base import Estimate, db_engine, Antibody, AntibodyToEstimate


def get_all_arbo_records():
    with Session(db_engine) as session:
        records = session.query(Estimate, func.array_agg(Antibody.antibody).label("antibodies")).\
            join(AntibodyToEstimate, Estimate.id == AntibodyToEstimate.estimate_id).\
            join(Antibody, Antibody.id == AntibodyToEstimate.antibody_id).\
            group_by(Estimate.id).all()

        print(f'[DEBUG] estimate record: {records[0]}')

        # Convert records to a list of dictionaries
        result_list = []
        for estimate, antibodies in records:
            record_dict = estimate.__dict__  # Convert Estimate object to a dictionary
            record_dict['antibodies'] = antibodies  # Add the 'antibodies' key
            result_list.append(record_dict)

        # Remove unnecessary attributes from the dictionaries
        for record_dict in result_list:
            record_dict.pop("_sa_instance_state")

        # Convert the list of dictionaries to JSON
        # Print or do whatever you want with the JSON data
        for record in result_list[0:5]:
            print(f'[DEBUG] estimate record: {record}')
            print("--------------------")

        return result_list


def get_all_arbo_filter_options():
    with Session(db_engine) as session:
        age_group = session.query(distinct(Estimate.age_group)).all()
        sex = session.query(distinct(Estimate.sex)).all()
        assay = session.query(distinct(Estimate.assay)).all()
        country = session.query(distinct(Estimate.country)).all()
        producer = session.query(distinct(Estimate.producer)).all()
        sample_frame = session.query(distinct(Estimate.sample_frame)).all()
        antibody = session.query(distinct(Antibody.antibody)).all()

        print(f'[DEBUG] age_group: {age_group[0]}')
        print(f'[DEBUG] antibody: {antibody[0]}')

        result_dict = {
            "age_group": [item[0] for item in age_group],
            "sex": [item[0] for item in sex],
            "assay": [item[0] for item in assay],
            "country": [item[0] for item in country],
            "producer": [item[0] for item in producer],
            "sample_frame": [item[0] for item in sample_frame],
            "antibody": [item[0] for item in antibody]
        }

        return result_dict
