import os
import logging.config
import multiprocessing

from flask import Flask
from flask_restplus import Api
from flask_cors import CORS
from .config import config_by_name
from flask_sqlalchemy import SQLAlchemy

logging.config.fileConfig(os.getenv('LOG_CONFIG_PATH'),
                        disable_existing_loggers=False,
                        defaults={'logfilename': os.getenv('LOG_FILE_PATH')})
logging.getLogger(__name__)


def create_app(db):
    # Initialize app and api
    app = Flask(__name__)
    api = Api(app)
    CORS(app)

    # Config app by dictionary in config file
    config_name = 'api_{}'.format(os.getenv('FLASK_ENV'))
    config_obj = config_by_name[config_name]
    app.config.from_object(config_obj)

    db.init_app(app)

    # Attach namespaces to api
    namespaces = config_obj.APP_NAMESPACES
    from .utils import init_namespace
    from .namespaces import healthcheck_ns, data_provider_ns, cases_count_scraper_ns,\
        meta_analysis_ns, test_adjustment_ns
    init_namespace(namespaces, api)

    app.app_context().push()
    return app


db = SQLAlchemy()
app = create_app(db)
multiprocessing.set_start_method("fork")
