import os


class ApiConfig:
    DEBUG = True
    APP_NAMESPACES = os.getenv('APP_NAMESPACES', ['airtable_scraper', 'healthcheck', 'data_provider',
                                                  'cases_count_scraper', 'meta_analysis', 'test_adjustment'])
    # Airtable config vars
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)
    AIRTABLE_SAMPLE_FRAME_GOI_OPTIONS_REQUEST_URL = "https://api.airtable.com/v0/appFfYIupTrVQ0HJx/Sample%20Frame%20GOI?fields=Order&fields=Name&sort%5B0%5D%5Bfield%5D=Order&fields=French%20Name"
    AIRTABLE_TIME_DIFF = os.getenv('AIRTABLE_TIME_DIFF', 24)
    AIRTABLE_CACHED_RESULTS_PATH = 'app/namespaces/data_provider/cached_results.json'

    # JHU config vars
    JHU_REQUEST_URL = "https://api.covid19api.com/summary"
    JHU_TIME_DIFF = os.getenv('JHU_TIME_DIFF', 24)
    JHU_CACHED_RESULTS_PATH = 'app/namespaces/cases_count_scraper/cached_results.json'

    # Meta analysis config vars
    MIN_DENOMINATOR = 200


class ApiDevelopmentConfig(ApiConfig):
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
    DATABASE_HOST_ADDRESS = 'localhost'
    DATABASE_NAME = 'whiteclaw'
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
                                        'postgresql://{username}:{password}@{host_address}:5432/{database_name}'.format(
                                            username=DATABASE_USERNAME,
                                            password=DATABASE_PASSWORD,
                                            host_address=DATABASE_HOST_ADDRESS,
                                            database_name=DATABASE_NAME))
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', True)
    def __init__(self):
        super(ApiConfig)


class ApiTestingConfig(ApiConfig):
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'postgres')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'postgres')
    DATABASE_HOST_ADDRESS = 'localhost'
    DATABASE_NAME = 'whiteclaw_test'
    SQLALCHEMY_DATABASE_URI = \
        f'postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST_ADDRESS}:5432/{DATABASE_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', True)

    def __init__(self):
        super(ApiConfig)


class ApiProductionConfig(ApiConfig):
    DEBUG = False
    PROPAGATE_EXCEPTIONS = False
    DATABASE_USERNAME = os.getenv('DATABASE_USERNAME')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
    DATABASE_HOST_ADDRESS = os.getenv('DATABASE_HOST_ADDRESS')
    DATABASE_NAME = 'whiteclaw'
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI',
                                        'postgresql://{username}:{password}@{host_address}:5432/{database_name}'.format(
                                            username=DATABASE_USERNAME,
                                            password=DATABASE_PASSWORD,
                                            host_address=DATABASE_HOST_ADDRESS,
                                            database_name=DATABASE_NAME))
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', True)
    def __init__(self):
        super(ApiConfig)


config_by_name = {'api_dev': ApiDevelopmentConfig, 'api_test': ApiTestingConfig, 'api_prod': ApiProductionConfig}
