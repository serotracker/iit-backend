import os


def test_environment_var_setup(app):
    flask_env = os.getenv('FLASK_ENV')
    assert flask_env == 'test'

    env_vars = [
        app.config['AIRTABLE_API_KEY'],
        app.config['AIRTABLE_BASE_ID'],
        os.getenv('MAPBOX_API_KEY'),
        os.getenv('LOG_FILE_PATH'),
        os.getenv('LOG_CONFIG_PATH')
    ]

    for env_var in env_vars:
        assert env_var is not None

    # make sure we are not hitting the prod database!
    assert app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite://"

