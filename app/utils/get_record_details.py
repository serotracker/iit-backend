import os

from app.serotracker_sqlalchemy import db_session, AirtableSource, Age, PopulationGroup, TestManufacturer, \
    ApprovingRegulator, TestType, AgeBridge, PopulationGroupBridge, \
    TestManufacturerBridge, ApprovingRegulatorBridge, TestTypeBridge
from sqlalchemy import create_engine, case, and_


# Create engine to connect to whiteclaw database
engine = create_engine('postgresql://{username}:{password}@localhost/whiteclaw'.format(
    username=os.getenv('DATABASE_USERNAME'),
    password=os.getenv('DATABASE_PASSWORD')))


def get_record_details(source_id):
    with db_session(engine) as session:
        try:
            isotype_case_expression = case(
                [
                    (and_(AirtableSource.isotype_igg == 'true',
                     AirtableSource.isotype_igm == 'true',
                     AirtableSource.isotype_iga == 'true'), 'IgG, IgM, IgA'),
                    (and_(AirtableSource.isotype_igg == 'true',
                     AirtableSource.isotype_igm == 'false',
                     AirtableSource.isotype_iga == 'true'), 'IgG, IgA'),
                    (and_(AirtableSource.isotype_igg == 'true',
                     AirtableSource.isotype_igm == 'true',
                     AirtableSource.isotype_iga == 'false'), 'IgG, IgM'),
                    (and_(AirtableSource.isotype_igg == 'false',
                     AirtableSource.isotype_igm == 'true',
                     AirtableSource.isotype_iga == 'true'), 'IgM, IgA'),
                    (and_(AirtableSource.isotype_igg == 'true',
                     AirtableSource.isotype_igm == 'false',
                     AirtableSource.isotype_iga == 'false'), 'IgG'),
                    (and_(AirtableSource.isotype_igg == 'false',
                     AirtableSource.isotype_igm == 'false',
                     AirtableSource.isotype_iga == 'true'), 'IgA'),
                    (and_(AirtableSource.isotype_igg == 'false',
                     AirtableSource.isotype_igm == 'true',
                     AirtableSource.isotype_iga == 'false'), 'IgM')], else_='').label("isotypes")
            query = session.query(AirtableSource.source_id,
                                  AirtableSource.source_name,
                                  AirtableSource.summary,
                                  AirtableSource.study_status,
                                  AirtableSource.sex,
                                  AirtableSource.serum_pos_prevalence,
                                  AirtableSource.denominator_value,
                                  AirtableSource.overall_risk_of_bias,
                                  AirtableSource.sampling_method,
                                  AirtableSource.sampling_start_date,
                                  AirtableSource.sampling_end_date,
                                  AirtableSource.country,
                                  AirtableSource.sensitivity,
                                  AirtableSource.specificity,
                                  Age.age_name,
                                  ApprovingRegulator.approving_regulator_name,
                                  TestManufacturer.test_manufacturer_name,
                                  TestType.test_type_name,
                                  PopulationGroup.population_group_name,
                                  isotype_case_expression) \
                .outerjoin(AgeBridge, AgeBridge.source_id == AirtableSource.source_id) \
                .outerjoin(Age, AgeBridge.age_id == Age.age_id) \
                .outerjoin(ApprovingRegulatorBridge, ApprovingRegulatorBridge.source_id == AirtableSource.source_id) \
                .outerjoin(ApprovingRegulator, ApprovingRegulatorBridge.approving_regulator_id
                           == ApprovingRegulator.approving_regulator_id) \
                .outerjoin(TestManufacturerBridge, TestManufacturerBridge.source_id == AirtableSource.source_id) \
                .outerjoin(TestManufacturer, TestManufacturerBridge.test_manufacturer_id
                           == TestManufacturer.test_manufacturer_id) \
                .outerjoin(TestTypeBridge, TestTypeBridge.source_id == AirtableSource.source_id) \
                .outerjoin(TestType, TestTypeBridge.test_type_id
                           == TestType.test_type_id) \
                .outerjoin(PopulationGroupBridge, PopulationGroupBridge.source_id == AirtableSource.source_id) \
                .outerjoin(PopulationGroup, PopulationGroupBridge.population_group_id
                           == PopulationGroup.population_group_id) \
                .filter(AirtableSource.source_id == source_id)
            result = query.all()
            result = [x._asdict() for x in result]
        except Exception as e:
            print(e)
    return result


if __name__ == '__main__':
    print(get_record_details('86f4e086-482a-48f8-a4d3-4adc45c6a1b0'))

