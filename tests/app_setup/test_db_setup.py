from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from app.serotracker_sqlalchemy import db_tables
from app.serotracker_sqlalchemy.models import AirtableSource, Age, AgeBridge, ApprovingRegulator, \
    ApprovingRegulatorBridge, City, CityBridge, PopulationGroup, PopulationGroupBridge, State, StateBridge, \
    SpecimenType, SpecimenTypeBridge, TestType, TestTypeBridge, TestManufacturer, TestManufacturerBridge


# def test_attached_db(db):
#     assert isinstance(db, SQLAlchemy)


def test_db_table_names():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    for table in db_tables:
        assert table in engine.table_names()


def test_empty_db(session):
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    with session(engine) as _session:
        assert len(_session.query(AirtableSource).all()) == 0

