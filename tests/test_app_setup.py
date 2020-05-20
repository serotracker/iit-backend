import os

from app import create_app


def test_flask_environment_variable():
    flask_env = os.getenv('FLASK_ENV')
    assert flask_env == 'test'


def test_app_namespaces(app):
    app_namespaces = app.config['APP_NAMESPACES']
    namespace_options = ['healthcheck', 'airtable_scraper']
    for namespace in namespace_options:
        assert namespace in namespace_options


def test_app_debug_variable(app):
    debug_var = app.config['DEBUG']
    assert debug_var is True


def test_airtable_credentials(app):
    airtable_api_key = app.config['AIRTABLE_API_KEY']
    airtable_base_id = app.config['AIRTABLE_BASE_ID']
    assert airtable_api_key is not None
    assert airtable_base_id is not None


def test_airtable_api_request_params(app):
    api_request_url = app.config['REQUEST_URL']
    api_request_params = app.config['REQUEST_PARAMS']
    assert type(api_request_url) is str
    assert type(api_request_params) is dict


def test_caching_refresh_variable(app):
    cache_refresh_hour_frequency = app.config['TIME_DIFF']
    assert cache_refresh_hour_frequency == 24


def test_create():
    app = create_app()
    assert app
    assert app.env == app.config['ENV'] == os.getenv('FLASK_ENV')
    assert app.config['AIRTABLE_API_KEY'] == os.getenv('AIRTABLE_API_KEY')
    assert app.config['TIME_DIFF'] == os.getenv('TIME_DIFF', 24)
