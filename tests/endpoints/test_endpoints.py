from app import db as _db
from app.serotracker_sqlalchemy.models import DashboardSource

def test_healthcheck(client):
    response = client.get('/healthcheck/')
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    assert type(data) is str
    assert data == 'The healthcheck endpoint was hit.'

# Test get records with an empty request body
def test_get_records_basic(client):
    response = client.post('/data_provider/records', json={
	    "filters": {}
    })
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    # Estimate prioritization should be applied by default so we should get 4 records back
    assert _db.session.query(DashboardSource).distinct(DashboardSource.study_name).count() == 4
    assert len(data) == 4


# Test get records with no estimate prioritization
def test_get_records_no_estimate_prioritization(client):
    response = client.post('/data_provider/records', json={
	    "filters": {},
        "prioritize_estimates": False
    })
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    assert _db.session.query(DashboardSource).count() == 14
    assert len(data) == 14