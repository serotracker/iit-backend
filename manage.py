import os
import subprocess

from app import create_app
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = create_app()
#CORS(app)


def run_app():
    if os.getenv('FLASK_ENV') == 'test':
        app.run()
    else:
        subprocess.call(['gunicorn', '--bind', '0.0.0.0:5000', 'wsgi:app'])


if __name__ == '__main__':
    run_app()
