import os

from flask import Flask
from flask_restplus import Api
from flask_cors import CORS

from .config import config_by_name
from .namespaces import healthcheck_ns, airtable_scraper_ns


def create_app():
    # Initialize app and api
    app = Flask(__name__)
    api = Api(app)
    CORS(app)

    # Config app by dictionary in config file
    config_name = 'api_{}'.format(os.getenv('FLASK_ENV'))
    config_obj = config_by_name[config_name]
    app.config.from_object(config_obj)

    # Attach namespaces to api
    api.add_namespace(healthcheck_ns)
    api.add_namespace(airtable_scraper_ns)

    app.app_context().push()

    return app

