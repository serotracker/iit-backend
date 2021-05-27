import tests.factories as factories

from app.serotracker_sqlalchemy import db_tables
from tests.utils import delete_records, delete_all_records, insert_full_recordset
from app.serotracker_sqlalchemy.models import DashboardSource, ResearchSource, AntibodyTarget, AntibodyTargetBridge, \
    City, CityBridge, State, StateBridge, TestManufacturer, TestManufacturerBridge, Country


def test_db_table_names(db):
    for table in db_tables:
        assert table in db.engine.table_names()


def test_empty_db(session):
    assert session.query(DashboardSource).count() == 0
    assert session.query(ResearchSource).count() == 0
    assert session.query(AntibodyTarget).count() == 0
    assert session.query(AntibodyTargetBridge).count() == 0
    assert session.query(City).count() == 0
    assert session.query(CityBridge).count() == 0
    assert session.query(State).count() == 0
    assert session.query(StateBridge).count() == 0
    assert session.query(TestManufacturer).count() == 0
    assert session.query(TestManufacturerBridge).count() == 0
    assert session.query(Country).count() == 0


# Tests inserting and deleting a single dashboard source record
# using our test helper functions
def test_one_dashboard_source_record(session):
    new_dashboard_source_record = factories.DashboardSourceFactory()
    all_dashboard_source_records = session.query(DashboardSource).all()
    assert [new_dashboard_source_record] == all_dashboard_source_records
    assert len(all_dashboard_source_records) == 1
    delete_records(session, all_dashboard_source_records)
    assert session.query(DashboardSource).count() == 0


# Tests inserting a complete record set
# using our test helper functions
def test_insert_recordset(session):
    insert_full_recordset(num_records=4)
    assert session.query(DashboardSource).count() == 4
    assert session.query(ResearchSource).count() == 4
    assert session.query(AntibodyTarget).count() == 1
    assert session.query(AntibodyTargetBridge).count() == 4
    assert session.query(City).count() == 1
    assert session.query(CityBridge).count() == 4
    assert session.query(State).count() == 1
    assert session.query(StateBridge).count() == 4
    assert session.query(TestManufacturer).count() == 1
    assert session.query(TestManufacturerBridge).count() == 4
    assert session.query(Country).count() == 1

    delete_all_records(session)
    for table in [DashboardSource, ResearchSource, Country, City, State, TestManufacturer, AntibodyTarget, CityBridge,
                  StateBridge, TestManufacturerBridge, AntibodyTargetBridge]:
        assert session.query(table).count() == 0
