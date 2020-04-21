import os
import subprocess

from flask_script import Manager

from app.init import app

manager = Manager(app)


@manager.command
def run():
    if os.getenv('FLASK_ENV') == 'test':
        app.run()
    else:
        subprocess.call(['gunicorn', '--bind', '0.0.0.0:5000', 'wsgi'])


if __name__ == '__main__':
    manager.run()
