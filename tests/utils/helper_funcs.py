import tests.factories as factories
import uuid
from app.serotracker_sqlalchemy import DashboardSource, ResearchSource, Country, City, State, \
    TestManufacturer, AntibodyTarget, CityBridge, StateBridge, TestManufacturerBridge, AntibodyTargetBridge


def delete_records(session, records):
    for record in records:
        session.delete(record)
    session.commit()
    return


def delete_all_records(session):
    for table in [DashboardSource, ResearchSource, Country, City, State, TestManufacturer, AntibodyTarget, CityBridge,
                  StateBridge, TestManufacturerBridge, AntibodyTargetBridge]:
        session.query(table).delete()
    session.commit()
    return


# Inserts a complete set of mocked dashboard records
# each sharing the same country, city, state, approving regulator, test manufacturer, and study
def insert_full_recordset(num_records=1, study_name="study"):
    # Insert records into non dashboard_source/research_source/bridge tables
    new_antibody_target_record = factories.AntibodyTargetFactory()
    antibody_target_id = new_antibody_target_record.antibody_target_id
    new_city_record = factories.CityFactory()
    city_id = new_city_record.city_id
    new_country_record = factories.CountryFactory()
    country_id = new_country_record.country_id
    new_state_record = factories.StateFactory()
    state_id = new_state_record.state_id
    new_test_manufacturer_record = factories.TestManufacturerFactory()
    test_manufacturer_id = new_test_manufacturer_record.test_manufacturer_id

    # Insert records into dashboard_source, research_source, and bridge tables
    for i in range(num_records):
        source_id = uuid.uuid4()
        # Ensure all are dashboard_primary estimates so that estimate prioritization
        # always returns 1 estimate per study
        factories.DashboardSourceFactory(source_id=source_id, country_id=country_id, study_name=study_name)
        factories.ResearchSourceFactory(source_id=source_id)
        factories.AntibodyTargetBridgeFactory(source_id=source_id, antibody_target_id=antibody_target_id)
        factories.CityBridgeFactory(source_id=source_id, city_id=city_id)
        factories.StateBridgeFactory(source_id=source_id, state_id=state_id)
        factories.TestManufacturerBridgeFactory(source_id=source_id, test_manufacturer_id=test_manufacturer_id)

    return
