import tests.factories as factories

from app.serotracker_sqlalchemy import db_tables
from tests.utils import delete_records, delete_all_records, insert_full_recordset
from app.serotracker_sqlalchemy.models import DashboardSource, ResearchSource, AntibodyTarget, AntibodyTargetBridge, \
    City, CityBridge, State, StateBridge, TestManufacturer, TestManufacturerBridge, Country


def test_db_table_names(db):
    for table in db_tables:
        assert table in db.engine.table_names()


def test_empty_db(session):
    assert len(session.query(DashboardSource).all()) == 0
    assert len(session.query(ResearchSource).all()) == 0
    assert len(session.query(AntibodyTarget).all()) == 0
    assert len(session.query(AntibodyTargetBridge).all()) == 0
    assert len(session.query(City).all()) == 0
    assert len(session.query(CityBridge).all()) == 0
    assert len(session.query(State).all()) == 0
    assert len(session.query(StateBridge).all()) == 0
    assert len(session.query(TestManufacturer).all()) == 0
    assert len(session.query(TestManufacturerBridge).all()) == 0
    assert len(session.query(Country).all()) == 0


# Tests inserting and deleting a single dashboard source record
# using our test helper functions
def test_one_dashboard_source_record(session):
    new_dashboard_source_record = factories.dashboard_source_factory(session)
    all_dashboard_source_records = session.query(DashboardSource).all()
    assert [new_dashboard_source_record] == all_dashboard_source_records
    assert len(all_dashboard_source_records) == 1
    delete_records(session, all_dashboard_source_records)
    assert len(session.query(DashboardSource).all()) == 0


# Tests inserting a complete record set
# using our test helper functions
def test_insert_recordset(session):
    insert_full_recordset(session, num_records=4)
    assert len(session.query(DashboardSource).all()) == 4
    assert len(session.query(ResearchSource).all()) == 4
    assert len(session.query(AntibodyTarget).all()) == 1
    assert len(session.query(AntibodyTargetBridge).all()) == 4
    assert len(session.query(City).all()) == 1
    assert len(session.query(CityBridge).all()) == 4
    assert len(session.query(State).all()) == 1
    assert len(session.query(StateBridge).all()) == 4
    assert len(session.query(TestManufacturer).all()) == 1
    assert len(session.query(TestManufacturerBridge).all()) == 4
    assert len(session.query(Country).all()) == 1

    delete_all_records(session)
    for table in [DashboardSource, ResearchSource, Country, City, State, TestManufacturer, AntibodyTarget, CityBridge,
                  StateBridge, TestManufacturerBridge, AntibodyTargetBridge]:
        assert len(session.query(table).all()) == 0
