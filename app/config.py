import os


class ApiConfig:
    DEBUG = True
    FLASK_DEBUG = True
    APP_NAMESPACES = os.getenv('APP_NAMESPACES', ['healthcheck', 'data_provider',
                                                  'cases_count_scraper', 'meta_analysis'])
    # Airtable config vars
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)
    AIRTABLE_REQUEST_PARAMS = {'filterByFormula': '{Visualize on SeroTracker?}=1'}
    AIRTABLE_TIME_DIFF = os.getenv('AIRTABLE_TIME_DIFF', 24)
    AIRTABLE_CACHED_RESULTS_PATH = 'app/namespaces/data_provider/cached_results.json'

    # JHU config vars
    JHU_REQUEST_URL = "https://api.covid19api.com/summary"
    JHU_TIME_DIFF = os.getenv('JHU_TIME_DIFF', 24)
    JHU_CACHED_RESULTS_PATH = 'app/namespaces/cases_count_scraper/cached_results.json'

    # Meta analysis config vars
    MIN_DENOMINATOR = 200


class ApiTestingConfig(ApiConfig):
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
    DATABASE_NAME = 'whiteclaw'
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
                                        'postgresql://{username}:{password}@localhost:5432/{database_name}'.format(
                                            username=DATABASE_USERNAME,
                                            password=DATABASE_PASSWORD,
                                            database_name=DATABASE_NAME))
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', True)
    def __init__(self):
        super(ApiConfig)


class ApiProductionConfig(ApiConfig):
    DEBUG = False
    FLASK_DEBUG = False

    def __init__(self):
        super(ApiConfig)


config_by_name = {'api_test': ApiTestingConfig, 'api_prod': ApiProductionConfig}
