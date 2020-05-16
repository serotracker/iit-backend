import json

import requests
import pandas as pd
import numpy as np

from flask import current_app as app


def add_fields_to_url(url):
    with open('app/utils/airtable_fields_config.json', 'r') as file:
        fields = json.load(file)
        for key in fields:
            url += 'fields%5B%5D={}&'.format(key)
    url = url[:-1]
    return url


def get_formatted_json_records(records):
    # Remove the created_at and id keys from each list item
    new_records = []
    for record in records:
        new_records.append(record['fields'])

    # Convert list of dictionaries to df
    total_records_df = pd.DataFrame(new_records)

    # Rename df columns according to formatted column names in config
    renamed_cols = {}
    with open('app/utils/airtable_fields_config.json', 'r') as file:
        fields = json.load(file)
        reordered_cols = []
        for value in fields.values():
            renamed_cols[value[0]] = value[1]
            reordered_cols.append(value[1])
    total_records_df = total_records_df.rename(columns=renamed_cols)
    total_records_df = total_records_df[reordered_cols]
    total_records_df = total_records_df.replace({np.nan: None})
    total_records_json = total_records_df.to_dict('records')
    return total_records_json


def get_all_records():
    url = app.config['REQUEST_URL']
    url = add_fields_to_url(url)
    headers = {'Authorization': 'Bearer {}'.format(app.config['AIRTABLE_API_KEY'])}
    params = app.config['REQUEST_PARAMS']
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    try:
        records = data['records']
        formatted_records = get_formatted_json_records(records)
        return formatted_records
    except KeyError:
        return "No records could be retrieved from Airtable."


def write_to_json(records):
    with open('cached_results.json', 'w') as file:
        json.dump(records, file)
    return


def read_from_json():
    with open('cached_results.json', 'r') as file:
        records = json.load(file)
    return records
