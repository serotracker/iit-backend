import os
import logging.config

from flask import Flask, render_template
from flask_restplus import Api
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import InternalServerError
from .config import config_by_name

logging.config.fileConfig('logging.cfg', disable_existing_loggers=False)
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

    # Connect db to app
    db.init_app(app)

    # Attach namespaces to api
    namespaces = config_obj.APP_NAMESPACES
    from .utils import init_namespace
    from .namespaces import airtable_scraper_ns, healthcheck_ns, data_provider_ns, cases_count_scraper_ns,\
        meta_analysis_ns
    init_namespace(namespaces, api)

    app.app_context().push()
    return app


db = SQLAlchemy()
app = create_app(db)

from .utils import send_slack_message


# @app.errorhandler(InternalServerError)
# def handle_500(e):
#     print('here')
#     original = getattr(e, "original_exception", None)
#     message = '@channel Internal Server Error: {}'.format(e)
#     send_slack_message(message=message, channel="#data-logging")
#     logging.error(e)
#
#     if original is None:
#         # direct 500 error, such as abort(500)
#         return render_template("500.html"), 500
#
#     # wrapped unhandled error
#     return render_template("500_unhandled.html", e=original), 500


# @app.after_request
# def test(response):
#     print('testing')
#     return response