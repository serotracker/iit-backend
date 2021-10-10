from app import db as _db
from app.serotracker_sqlalchemy.models import DashboardSource


def test_healthcheck(client):
    response = client.get('/healthcheck/')
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    assert type(data) is str


# Test get filter options
def test_get_filter_options(client):
    response = client.get('/data_provider/filter_options')
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    assert type(data) is dict


# Test get records details
def test_get_record_details(client):
    source_id = str(_db.session.query(DashboardSource.source_id).all()[0][0])
    response = client.get(f'/data_provider/record_details/{source_id}')
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    assert type(data) is dict


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
    assert len(data["records"]) == 4
    assert len(data["country_seroprev_summary"]) == 4


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
    assert len(data["records"]) == 14


# Test get records with country filters
def test_get_records_country_filter(client):
    response = client.post('/data_provider/records', json={
	    "filters": {
            "country": ["country_name_1", "country_name_2"]
        }
    })
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    assert len(data["records"]) == 2
    assert len(data["country_seroprev_summary"]) == 2


# Test get records with research fields
def test_get_records_research_fields(client):
    response = client.post('/data_provider/records', json={
	    "filters": {},
        "research_fields": True
    })
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    assert len(data["records"]) == 4
    # check if some field in the research table is in the returned record
    for record in data["records"]:
        assert "adj_sensitivity" in record