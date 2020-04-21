import os


class ApiConfig:
    DEBUG = True
    FLASK_DEBUG = True
    APP_NAMESPACES = os.getenv('APP_NAMESPACES', ['healthcheck', 'airtable_scraper'])
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY', 'yourkey')
    AIRTABLE_BASE_NAME = os.getenv('AIRTABLE_BASE_NAME', 'basename')


class ApiTestingConfig(ApiConfig):
    def __init__(self):
        super(ApiConfig)


class ApiProductionConfig(ApiConfig):
    DEBUG = False
    FLASK_DEBUG = False

    def __init__(self):
        super(ApiConfig)


config_by_name = {'api_test': ApiTestingConfig, 'api_prod': ApiProductionConfig}