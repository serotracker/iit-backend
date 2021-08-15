import os
import subprocess

from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_script import Manager
from app import app, db

load_dotenv()
manager = Manager(app)
migrate = Migrate(app, db, compare_type=True)


@manager.command
def run():
    if os.getenv('FLASK_ENV') == 'dev':
        app.run()
    else:
        subprocess.call(['gunicorn', '--bind', '0.0.0.0:5000', 'wsgi:app'])


@manager.shell
def make_shell_context():
    from flask_sqlalchemy import get_debug_queries
    from app.serotracker_sqlalchemy.models import DashboardSource
    return dict(app=app, db=db, gq=get_debug_queries(), DashboardSource=DashboardSource)


@manager.command
def test():
    if os.getenv('FLASK_ENV') == 'test':
        # Only run test_utils in the /test_utils directory
        subprocess.call(['pytest', '-vv'])
    else:
        print('Set FLASK_ENV = \'test\' and run again.')


if __name__ == '__main__':
    manager.run()
