from app.utils import airtable_fields_config


def test_airtable_fields_config():
    fields = airtable_fields_config['dashboard']
    assert type(fields) is dict


def test_get_airtable_records(client):
    # Make request and get response
    response = client.get('airtable_scraper/records')
    data = response.get_json()
    assert type(data) is dict
    assert response.status_code == 200

    # Check response keys are correct
    keys = data.keys()
    response_fields = ['airtable_request_status_code', 'records', 'updated_at']
    for key in keys:
        assert key in response_fields

    # Check response value types are correct
    assert type(data['airtable_request_status_code']) is int
    assert type(data['records']) is list
    assert type(data['updated_at']) is str


def test_get_airtable_records_correct_config(client):
    # Make request and check response has successful airtable request status code
    response = client.get('airtable_scraper/records')
    data = response.get_json()
    airtable_request_status_code = data['airtable_request_status_code']
    assert airtable_request_status_code == 200

    # Make sure records fields in response are same as fields in config
    response_records_fields = list(data['records'][0].keys())
    config_fields = list(airtable_fields_config['dashboard'].values())
    assert len(response_records_fields) == len(config_fields)
    for field in response_records_fields:
        assert field in config_fields


