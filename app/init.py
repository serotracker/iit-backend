import os

from flask import Flask
from flask_restplus import Api

from .config import config_by_name
from .utils.init import init_namespace


def create_app():
    # Initialize app and api
    app = Flask(__name__)
    api = Api()

    # Config app by dictionary in config file
    config_name = 'api_{}'.format(os.getenv('FLASK_ENV'))
    config_obj = config_by_name[config_name]
    app.config.from_object(config_obj)

    # Set namespaces to attach to api
    namespaces = config_obj.APP_NAMESPACES
    init_namespace(namespaces, api)

    return app


app = create_app()

