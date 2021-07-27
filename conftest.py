import pytest

from app import create_app, db as _db
from test_utils import insert_full_recordset, delete_all_records


@pytest.fixture(scope='session')
def app():
    app = create_app(_db)
    yield app


@pytest.fixture(scope='session')
def db(app):
    _db.create_all()
    yield _db
    _db.session.close_all()
    _db.drop_all()


# Pytest fixture that inserts a realistic set of records
# and yields a client so that we can test endpoints
# make db an argument to ensure that the client fixture is run after the db and app fixtures are run
@pytest.fixture(scope='module')
def client(db, app):
    insert_full_recordset(num_records=4, study_name="study_a")
    insert_full_recordset(num_records=2, study_name="study_b")
    insert_full_recordset(num_records=1, study_name="study_c")
    insert_full_recordset(num_records=7, study_name="study_d")
    yield app.test_client()
    delete_all_records(_db.session)
