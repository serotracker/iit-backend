import json
import logging

import requests
import pandas as pd
import numpy as np

from flask import current_app as app
from app.utils import read_from_json, send_api_error_email, airtable_fields_config

logger = logging.getLogger(__name__)


def _add_fields_to_url(url, airtable_json='dashboard'):
    # Get airtable fields json object according to json type: dashboard or research
    fields = airtable_fields_config[airtable_json]
    # Add fields in config to api URL
    for key in fields:
        url += 'fields%5B%5D={}&'.format(key)
    url = url[:-1]
    return url


def _get_formatted_json_records(records, airtable_json='dashboard'):
    # Remove the created_at and id keys from each list item
    new_records = [record['fields'] for record in records]

    # Convert list of dictionaries to df
    total_records_df = pd.DataFrame(new_records)

    # Rename and reorder df columns according to formatted column names in config
    fields = airtable_fields_config[airtable_json]
    renamed_cols = {key: fields[key] for key in fields}
    reordered_cols = [fields[key] for key in fields]
    total_records_df = total_records_df.rename(columns=renamed_cols)
    total_records_df = total_records_df[reordered_cols]
    total_records_df = total_records_df.replace({np.nan: None})
    total_records_json = total_records_df.to_dict('records')
    return total_records_json


def _get_paginated_records(data, api_request_info):
    # Extract API request parameters
    url = api_request_info[0]
    headers = api_request_info[1]
    parameters = api_request_info[2]

    # Extract records from initial request response
    records = data['records']

    # Continue adding paginated records so long as there is an offset in the api response
    while 'offset' in list(data.keys()):
        parameters['offset'] = data['offset']
        r = requests.get(url, headers=headers, params=parameters)
        data = r.json()
        records += data['records']
    return records


def get_all_records(visualize_sero_filter, airtable_fields_json):
    # Get airtable API URL and add fields to be scraped to URL in HTML format
    url = app.config['AIRTABLE_REQUEST_URL']
    url = _add_fields_to_url(url, airtable_fields_json)
    headers = {'Authorization': 'Bearer {}'.format(app.config['AIRTABLE_API_KEY'])}
    params = app.config['AIRTABLE_REQUEST_PARAMS'] if visualize_sero_filter else None

    # Make request and retrieve records in json format
    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    # Try to get records from data if the request was successful
    try:
        # If offset was included in data, retrieve additional paginated records
        if 'offset' in list(data.keys()):
            parameters = params.copy() if params is not None else {}
            request_info = [url, headers, parameters]
            records = _get_paginated_records(data, request_info)
        else:
            records = data['records']
        formatted_records = _get_formatted_json_records(records)
        return formatted_records, 200

    # If request was not successful, there will be no records field in response
    # Just return what is in cached layer and log an error
    except KeyError as e:
        body = "Results were not successfully retrieved from Airtable API." \
               "Please check connection parameters in config.py and fields in airtable_fields_config.py."
        logger.error(body)
        logger.error(f"Error Info: {e}")
        logger.error(f"API Response Info: {data}")

        request_info = {
            "url": url,
            "headers": json.dumps(headers)
        }

        send_api_error_email(body, data, error=e, request_info=request_info)

        try:
            records = read_from_json(app.config['AIRTABLE_CACHED_RESULTS_PATH'])
        except FileNotFoundError:
            records = []
        return records, 400

