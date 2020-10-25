from app.utils import airtable_fields_config
from tests.utils import delete_records, insert_record


def test_airtable_fields_config():
    fields = airtable_fields_config['dashboard']
    assert type(fields) is dict


def test_get_airtable_records(client, session):
    with session() as _session:
        # Insert a record
        insert_record(_session)
        # Make request and get response
        response = client.get('data_provider/records')
        data = response.get_json()
        # Check that the response status is good
        assert response.status_code == 200
        # Check that a list containing on record dict is returned
        assert type(data) is list
        assert len(data) == 1
        assert type(data[0]) == dict
