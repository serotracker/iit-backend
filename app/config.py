import os


class ApiConfig:
    DEBUG = True
    FLASK_DEBUG = True
    APP_NAMESPACES = os.getenv('APP_NAMESPACES', ['healthcheck', 'airtable_scraper', 'cases_count_scraper'])
    AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
    AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)
    AIRTABLE_REQUEST_PARAMS = {'filterByFormula': '{Visualize on SeroTracker?}=1'}
    AIRTABLE_TIME_DIFF = os.getenv('TIME_DIFF', 24)
    JHU_REQUEST_URL = "https://api.covid19api.com/summary"
    JHU_TIME_DIFF = os.getenv('TIME_DIFF', 24)


class ApiTestingConfig(ApiConfig):
    def __init__(self):
        super(ApiConfig)


class ApiProductionConfig(ApiConfig):
    DEBUG = False
    FLASK_DEBUG = False

    def __init__(self):
        super(ApiConfig)


config_by_name = {'api_test': ApiTestingConfig, 'api_prod': ApiProductionConfig}
