import os


class ApiConfig:
    DEBUG = True
    FLASK_DEBUG = True
    APP_NAMESPACES = os.getenv('APP_NAMESPACES', ['healthcheck', 'airtable_scraper'])
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    BASE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%20Data?filterByFormula=" \
                       "%7BMeets+Inclusion+Criteria%3F%7D%3D%22Yes%22".format(AIRTABLE_BASE_ID)


class ApiTestingConfig(ApiConfig):
    def __init__(self):
        super(ApiConfig)


class ApiProductionConfig(ApiConfig):
    DEBUG = False
    FLASK_DEBUG = False

    def __init__(self):
        super(ApiConfig)


config_by_name = {'api_test': ApiTestingConfig, 'api_prod': ApiProductionConfig}
