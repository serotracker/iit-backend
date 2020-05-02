import json

import requests

from flask import current_app as app


def get_all_records():
    url = app.config['BASE_REQUEST_URL']
    headers = {"Authorization": "Bearer {}".format(app.config['AIRTABLE_API_KEY'])}
    params = app.config['AIRTABLE_FIELDS']
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    records = data['records']
    return records


def write_to_json(records):
    with open('cached_results.json', 'w') as file:
        json.dump(records, file)
    return


def read_from_json():
    with open('cached_results.json', 'r') as file:
        records = json.load(file)
    return records
