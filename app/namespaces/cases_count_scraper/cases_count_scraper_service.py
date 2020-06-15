import json
import logging

import requests

from flask import current_app as app

logger = logging.getLogger(__name__)


def get_all_records():
    # Get URL for API request
    url = app.config['JHU_REQUEST_URL']

    # Make request and retrieve records in json format
    r = requests.get(url)
    data = r.json()
    status_code = r.status_code

    # If status code is not 200, read records in cached json layer
    if status_code != 200:
        data = read_from_json()

    return data, status_code


def write_to_json(records):
    with open('app/namespaces/cases_count_scraper/cached_results.json', 'w') as file:
        json.dump(records, file)
    return


def read_from_json():
    with open('app/namespaces/cases_count_scraper/cached_results.json', 'r') as file:
        records = json.load(file)
    return records
