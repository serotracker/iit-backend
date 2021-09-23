import requests
import json
import logging
from uuid import uuid4

import pandas as pd
from sqlalchemy.sql.sqltypes import String
from flask import current_app as app

from app.utils import full_airtable_fields, send_api_error_slack_notif
from datetime import datetime
from app.serotracker_sqlalchemy import db_session
from app.serotracker_sqlalchemy.models import PopulationGroupOptions

AIRTABLE_API_KEY = app.config['AIRTABLE_API_KEY']
AIRTABLE_BASE_ID = app.config['AIRTABLE_BASE_ID']
AIRTABLE_REQUEST_URL = app.config['AIRTABLE_REQUEST_URL']
AIRTABLE_SAMPLE_FRAME_GOI_OPTIONS_REQUEST_URL = app.config['AIRTABLE_SAMPLE_FRAME_GOI_OPTIONS_REQUEST_URL']


def add_fields_to_url(url, fields):
    # Add fields to api URL
    for key in fields:
        url += 'fields%5B%5D={}&'.format(key)
    url = url[:-1]
    return url


def airtable_get_request(url: String, headers):
    # Make request and retrieve records in json format
    r = requests.get(url, headers=headers)
    data = r.json()
    return data


def handle_airtable_error(e: KeyError, data, url: String, headers):
    body = "Results were not successfully retrieved from Airtable API. " \
           "Please check connection parameters in config.py and fields in airtable_fields_config.json."
    request_info = {
        "url": url,
        "headers": json.dumps(headers)
    }
    logging.error(e)
    send_api_error_slack_notif(body, data, error=e, request_info=request_info, channel='#dev-logging-etl')
    return


def get_formatted_json_records(records):
    # Remove the created_at and id keys from each list item
    new_records = [record['fields'] for record in records]

    # Convert list of dictionaries to df
    total_records_df = pd.DataFrame(new_records)

    # Rename and reorder df columns according to formatted column names in config
    renamed_cols = full_airtable_fields
    total_records_df = total_records_df.rename(columns=renamed_cols)
    total_records_df = total_records_df.where(total_records_df.notna(), None)
    total_records_json = total_records_df.to_dict('records')
    return total_records_json


def get_paginated_records(data, api_request_info):
    # Extract API request parameters
    url = api_request_info[0]
    headers = api_request_info[1]

    # Extract records from initial request response
    records = data['records']

    # Continue adding paginated records so long as there is an offset in the api response
    while 'offset' in list(data.keys()):
        r = requests.get(url, headers=headers, params={'offset': data['offset']})
        data = r.json()
        records += data['records']
    return records


def get_all_records(fields):
    # Get airtable API URL and add fields to be scraped to URL in HTML format
    headers = {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}
    url = AIRTABLE_REQUEST_URL.format(AIRTABLE_BASE_ID)
    url = add_fields_to_url(url, fields)
    url += '&filterByFormula={ETL Included}=1'
    data = airtable_get_request(url, headers)

    # Try to get records from data if the request was successful
    try:
        # If offset was included in data, retrieve additional paginated records
        if 'offset' in list(data.keys()):
            request_info = [url, {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}]
            records = get_paginated_records(data, request_info)
        else:
            records = data['records']
        formatted_records = get_formatted_json_records(records)
        return formatted_records

    # If request was not successful, there will be no records field in response
    # Just return what is in cached layer and log an error
    except KeyError as e:
        handle_airtable_error(e, data, url, headers)
    return


'''
Updates population_group_options table in whiteclaw with entries from Sample Frame GOI table in Serosurveillance Base in Airtable (name, french translation and order).
These records will be used for the "Population group" filters on serotracker.com.
'''


def ingest_sample_frame_goi_filter_options():
    headers = {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}
    data = airtable_get_request(AIRTABLE_SAMPLE_FRAME_GOI_OPTIONS_REQUEST_URL, headers)
    # Try to get records from data if the request was successful
    try:
        # Get sorted records
        records = data["records"]
        current_time = datetime.now()
        # Add records to table 
        with db_session() as session:
            records_to_add = [PopulationGroupOptions(id=uuid4(),
                                                     name=record['fields']['Name'],
                                                     french_name=record['fields']['French Name'] if 'French Name' in
                                                                 record['fields'] else None,
                                                     order=record['fields']['Order'] if 'Order' in record[
                                                         'fields'] else None,
                                                     created_at=current_time)
                              for record in records if record['fields']]
            session.bulk_save_objects(records_to_add)
            session.commit()
        return
    except KeyError as e:
        handle_airtable_error(e, data, AIRTABLE_SAMPLE_FRAME_GOI_OPTIONS_REQUEST_URL, headers)
        return
