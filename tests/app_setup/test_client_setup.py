def test_client(client):
    response = client.get('/healthcheck/')
    status_code = response.status_code
    data = response.get_json()
    assert status_code == 200
    assert type(data) is str
    assert data == 'The healthcheck endpoint was hit.'
