import pytest

from app import create_app, db as _db
from app.serotracker_sqlalchemy import db_session


@pytest.fixture(scope='session')
def app():
    app = create_app(db=_db)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def db():
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='function')
def session():
    return db_session
