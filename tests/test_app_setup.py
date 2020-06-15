import os

from app import create_app


def test_flask_environment_variable():
    flask_env = os.getenv('FLASK_ENV')
    assert flask_env == 'test'


def test_app_namespaces(app):
    app_namespaces = app.config['APP_NAMESPACES']
    namespace_options = ['healthcheck', 'airtable_scraper', 'cases_count_scraper']
    for namespace in app_namespaces:
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
    api_request_url = app.config['AIRTABLE_REQUEST_URL']
    api_request_params = app.config['AIRTABLE_REQUEST_PARAMS']
    assert type(api_request_url) is str
    assert type(api_request_params) is dict


def test_jhu_api_request_params(app):
    api_request_url = app.config['JHU_REQUEST_URL']
    assert type(api_request_url) is str


def test_caching_refresh_variables(app):
    airtable_cache_refresh_hour_frequency = app.config['AIRTABLE_TIME_DIFF']
    jhu_cache_refresh_hour_frequency = app.config['JHU_TIME_DIFF']
    assert airtable_cache_refresh_hour_frequency == 24
    assert jhu_cache_refresh_hour_frequency == 24

