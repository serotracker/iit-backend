import requests

from flask import current_app as app
from flask import jsonify


def get_all_records():
    url = app.config['BASE_REQUEST_URL']
    headers = {"Authorization": "Bearer {}".format(app.config['AIRTABLE_API_KEY'])}
    r = requests.get(url, headers=headers)
    data = r.json()
    records = data['records']
    return jsonify(records)
