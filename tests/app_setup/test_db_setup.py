from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import tests.factories as factories

from app.serotracker_sqlalchemy import db_tables, delete_records
from app.serotracker_sqlalchemy.models import AirtableSource, Age, AgeBridge, ApprovingRegulator, \
    ApprovingRegulatorBridge, City, CityBridge, PopulationGroup, PopulationGroupBridge, State, StateBridge, \
    SpecimenType, SpecimenTypeBridge, TestType, TestTypeBridge, TestManufacturer, TestManufacturerBridge


def test_attached_db(db):
    assert isinstance(db, SQLAlchemy)


def test_db_table_names():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    for table in db_tables:
        assert table in engine.table_names()


def test_empty_db(session):
    with session() as _session:
        assert len(_session.query(AirtableSource).all()) == 0
        assert len(_session.query(Age).all()) == 0
        assert len(_session.query(AgeBridge).all()) == 0
        assert len(_session.query(ApprovingRegulator).all()) == 0
        assert len(_session.query(ApprovingRegulatorBridge).all()) == 0
        assert len(_session.query(City).all()) == 0
        assert len(_session.query(CityBridge).all()) == 0
        assert len(_session.query(PopulationGroup).all()) == 0
        assert len(_session.query(PopulationGroupBridge).all()) == 0
        assert len(_session.query(State).all()) == 0
        assert len(_session.query(StateBridge).all()) == 0
        assert len(_session.query(SpecimenType).all()) == 0
        assert len(_session.query(SpecimenTypeBridge).all()) == 0
        assert len(_session.query(TestType).all()) == 0
        assert len(_session.query(TestTypeBridge).all()) == 0
        assert len(_session.query(TestManufacturer).all()) == 0
        assert len(_session.query(TestManufacturerBridge).all()) == 0


def test_one_airtable_source_record(session):
    with session() as _session:
        new_airtable_source_record = factories.airtable_source_factory(_session)
        all_airtable_source_records = _session.query(AirtableSource).all()
        assert [new_airtable_source_record] == all_airtable_source_records
        assert len(all_airtable_source_records) == 1
        delete_records(_session, all_airtable_source_records)
