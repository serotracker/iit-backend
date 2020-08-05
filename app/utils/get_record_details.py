import os

from app.serotracker_sqlalchemy import db_session, AirtableSource, Age, PopulationGroup, TestManufacturer, \
    ApprovingRegulator, TestType, AgeBridge, PopulationGroupBridge, \
    TestManufacturerBridge, ApprovingRegulatorBridge, TestTypeBridge
from sqlalchemy import create_engine, case


# Create engine to connect to whiteclaw database
engine = create_engine('postgresql://{username}:{password}@localhost/whiteclaw'.format(
    username=os.getenv('DATABASE_USERNAME'),
    password=os.getenv('DATABASE_PASSWORD')))


def get_record_details(source_id):
    with db_session(engine) as session:
        try:
            # result = session.query(AirtableSource.source_id, AirtableSource.source_name, Age.age_id, Age.age_name) \
            #     .join(AgeBridge, AgeBridge.source_id == AirtableSource.source_id) \
            #     .join(Age, AgeBridge.age_id==Age.age_id).all()
            # isotype_case_expression = case(
            #     [
            #         (AirtableSource.isotype_igg.is_(True)
            #          and AirtableSource.isotype_igm.is_(True)
            #          and AirtableSource.isotype_iga.is_(True), 'IgG, IgM, IgA'),
            #         (AirtableSource.isotype_igg.is_(True)
            #          and AirtableSource.isotype_igm.is_(False)
            #          and AirtableSource.isotype_iga.is_(True), 'IgG, IgA'),
            #         (AirtableSource.isotype_igg.is_(True)
            #          and AirtableSource.isotype_igm.is_(True)
            #          and AirtableSource.isotype_iga.is_(False), 'IgG, IgM'),
            #         (AirtableSource.isotype_igg.is_(False)
            #          and AirtableSource.isotype_igm.is_(True)
            #          and AirtableSource.isotype_iga.is_(True), 'IgM, IgA'),
            #         (AirtableSource.isotype_igg.is_(True)
            #          and AirtableSource.isotype_igm.is_(False)
            #          and AirtableSource.isotype_iga.is_(False), 'IgG'),
            #         (AirtableSource.isotype_igg.is_(False)
            #          and AirtableSource.isotype_igm.is_(False)
            #          and AirtableSource.isotype_iga.is_(True), 'IgA'),
            #         (AirtableSource.isotype_igg.is_(False)
            #          and AirtableSource.isotype_igm.is_(True)
            #          and AirtableSource.isotype_iga.is_(False), 'IgM')
            #     ]).label("isotypes")
            # query = session.query(AirtableSource.source_id,
            #                       AirtableSource.source_name,
            #                       AirtableSource.summary,
            #                       AirtableSource.study_status,
            #                       AirtableSource.sex,
            #                       AirtableSource.serum_pos_prevalence,
            #                       AirtableSource.denominator_value,
            #                       AirtableSource.overall_risk_of_bias,
            #                       AirtableSource.sampling_method,
            #                       AirtableSource.sampling_start_date,
            #                       AirtableSource.sampling_end_date,
            #                       AirtableSource.country,
            #                       AirtableSource.sensitivity,
            #                       AirtableSource.specificity,
            #                       Age.age_name,
            #                       ApprovingRegulator.approving_regulator_name,
            #                       TestManufacturer.test_manufacturer_name,
            #                       TestType.test_type_name,
            #                       PopulationGroup.population_group_name,
            #                       isotype_case_expression) \
            #     .outerjoin(AgeBridge, AgeBridge.source_id == AirtableSource.source_id) \
            #     .outerjoin(Age, AgeBridge.age_id == Age.age_id) \
            #     .outerjoin(ApprovingRegulatorBridge, ApprovingRegulatorBridge.source_id == AirtableSource.source_id) \
            #     .outerjoin(ApprovingRegulator, ApprovingRegulatorBridge.approving_regulator_id
            #                == ApprovingRegulator.approving_regulator_id) \
            #     .outerjoin(TestManufacturerBridge, TestManufacturerBridge.source_id == AirtableSource.source_id) \
            #     .outerjoin(TestManufacturer, TestManufacturerBridge.test_manufacturer_id
            #                == TestManufacturer.test_manufacturer_id) \
            #     .outerjoin(TestTypeBridge, TestTypeBridge.source_id == AirtableSource.source_id) \
            #     .outerjoin(TestType, TestTypeBridge.test_type_id
            #                == TestType.test_type_id) \
            #     .outerjoin(PopulationGroupBridge, PopulationGroupBridge.source_id == AirtableSource.source_id) \
            #     .outerjoin(PopulationGroup, PopulationGroupBridge.population_group_id
            #                == PopulationGroup.population_group_id) \
            #     .filter(AirtableSource.source_id == source_id)
            query = session.query(AirtableSource).filter(AirtableSource.source_id == source_id)
            print(query)
            result = query.all()
            print(result)
            for r in result:
                print(r)
                print(type(r))
                print(r._asdict())
        except Exception as e:
            print(e)
        print(result)
        result = [x._asdict() for x in result]
        print(result)
    return

if __name__ == '__main__':
    get_record_details('86f4e086-482a-48f8-a4d3-4adc45c6a1b0')


