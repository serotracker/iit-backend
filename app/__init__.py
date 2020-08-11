import os

from flask import Flask
from flask_restplus import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from .config import config_by_name
from .namespaces import healthcheck_ns, data_provider_ns, cases_count_scraper_ns, meta_analysis_ns
from .utils import init_namespace


def create_app(db):
    # Initialize app and api
    app = Flask(__name__)
    api = Api(app)
    CORS(app)

    # Config app by dictionary in config file
    config_name = 'api_{}'.format(os.getenv('FLASK_ENV'))
    config_obj = config_by_name[config_name]
    app.config.from_object(config_obj)

    # Connect db to app
    db.init_app(app)

    # Attach namespaces to api
    namespaces = config_obj.APP_NAMESPACES
    init_namespace(namespaces, api)

    app.app_context().push()
    return app


db = SQLAlchemy()
app = create_app(db)
