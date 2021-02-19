from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import tests.factories as factories

from app.serotracker_sqlalchemy import db_tables
from tests.utils import delete_records
from app.serotracker_sqlalchemy.models import DashboardSource, ResearchSource, AntibodyTarget, AntibodyTargetBridge, \
    City, CityBridge, State, StateBridge, TestManufacturer, TestManufacturerBridge


def test_attached_db(db):
    assert isinstance(db, SQLAlchemy)


def test_db_table_names():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    for table in db_tables:
        assert table in engine.table_names()


def test_empty_db(session):
    with session() as _session:
        assert len(_session.query(DashboardSource).all()) == 0
        assert len(_session.query(ResearchSource).all()) == 0
        assert len(_session.query(AntibodyTarget).all()) == 0
        assert len(_session.query(AntibodyTargetBridge).all()) == 0
        assert len(_session.query(City).all()) == 0
        assert len(_session.query(CityBridge).all()) == 0
        assert len(_session.query(State).all()) == 0
        assert len(_session.query(StateBridge).all()) == 0
        assert len(_session.query(TestManufacturer).all()) == 0
        assert len(_session.query(TestManufacturerBridge).all()) == 0


def test_one_dashboard_source_record(session):
    with session() as _session:
        new_dashboard_source_record = factories.dashboard_source_factory(_session)
        all_dashboard_source_records = _session.query(DashboardSource).all()
        assert [new_dashboard_source_record] == all_dashboard_source_records
        assert len(all_dashboard_source_records) == 1
        delete_records(_session, all_dashboard_source_records)
