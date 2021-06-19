import os


def test_app_setup(app):
    flask_env = os.getenv('FLASK_ENV')
    assert flask_env == 'test'

    # make sure we are not hitting the prod database!
    assert app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1] == "whiteclaw_test"

