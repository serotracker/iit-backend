import os

from app import create_app

def test_create():
    app = create_app()
    assert app == False  # TO BE REMOVED
    assert app.env == app.config['ENV'] == os.getenv('FLASK_ENV')
    assert app.config['AIRTABLE_API_KEY'] == os.getenv('AIRTABLE_API_KEY')
    assert app.config['TIME_DIFF'] == os.getenv('TIME_DIFF', 24)
