import os
import subprocess

from dotenv import load_dotenv
from flask_script import Manager
from app import app, db

load_dotenv()
manager = Manager(app)


@manager.command
def run():
    if os.getenv('FLASK_ENV') == 'test':
        app.run()
    else:
        subprocess.call(['gunicorn', '--bind', '0.0.0.0:5000', 'wsgi:app'])


@manager.shell
def make_shell_context():
    from flask_sqlalchemy import get_debug_queries
    from app.serotracker_sqlalchemy.models import AirtableSource
    return dict(app=app, db=db, gq=get_debug_queries(), AirtableSource=AirtableSource)


@manager.command
def test():
    if os.getenv('FLASK_ENV') == 'test':
        subprocess.call(['pytest', '-vv'])
    else:
        print('Set FLASK_ENV = \'test\' and run again.')


if __name__ == '__main__':
    manager.run()
