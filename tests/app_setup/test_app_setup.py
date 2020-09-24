import os


def test_flask_environment_variable():
    flask_env = os.getenv('FLASK_ENV')
    assert flask_env == 'test'


def test_app_namespaces(app):
    app_namespaces = app.config['APP_NAMESPACES']
    namespace_options = ['healthcheck', 'data_provider', 'cases_count_scraper', 'meta_analysis']
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


def test_cached_results_path(app):
    airtable_cached_results_path = app.config['AIRTABLE_CACHED_RESULTS_PATH']
    jhu_cached_results_path = app.config['JHU_CACHED_RESULTS_PATH']
    assert airtable_cached_results_path is not None
    assert jhu_cached_results_path is not None


def test_meta_analysis_vars(app):
    min_denominator = app.config['MIN_DENOMINATOR']
    assert min_denominator == 200


def test_db_variables(app):
    db_username = app.config['DATABASE_USERNAME']
    db_pass = app.config['DATABASE_PASSWORD']
    db_host = app.config['DATABASE_HOST']
    db_name = app.config['DATABASE_NAME']
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_track_modifications = app.config['SQLALCHEMY_TRACK_MODIFICATIONS']
    assert db_username is not None
    assert db_pass is not None
    assert db_name is not None
    assert db_uri is not None
    assert db_track_modifications is not None
