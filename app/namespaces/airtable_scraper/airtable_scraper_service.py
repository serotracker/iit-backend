import json
import logging
import os
import smtplib
import ssl

from email.mime.text import MIMEText

import requests
import pandas as pd
import numpy as np

from flask import current_app as app

logger = logging.getLogger(__name__)

# SMTP setup
port = 465
context = ssl.create_default_context()
sender = 'iitbackendalerts@gmail.com'
recipients = ['abeljohnjoseph@gmail.com', 'ewanmay3@gmail.com', 'simonarocco09@gmail.com', 'austin.atmaja@gmail.com']  # Add additional email addresses here
password = os.getenv('GMAIL_PASS')


def _add_fields_to_url(url):
    # Add fields in config to api URL
    with open('app/utils/airtable_fields_config.json', 'r') as file:
        fields = json.load(file)
        for key in fields:
            url += 'fields%5B%5D={}&'.format(key)
    url = url[:-1]
    return url


def _get_formatted_json_records(records):
    # Remove the created_at and id keys from each list item
    new_records = [record['fields'] for record in records]

    # Convert list of dictionaries to df
    total_records_df = pd.DataFrame(new_records)

    # Rename and reorder df columns according to formatted column names in config
    with open('app/utils/airtable_fields_config.json', 'r') as file:
        fields = json.load(file)
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
    params = api_request_info[2]

    # Extract records from initial request response
    records = data['records']

    # Continue adding paginated records so long as there is an offset in the api response
    while 'offset' in list(data.keys()):
        params['offset'] = data['offset']
        r = requests.get(url, headers=headers, params=params)
        data = r.json()
        records += data['records']
    return records


def get_all_records():
    # Get airtable API URL and add fields to be scraped to URL in HTML format
    url = app.config['REQUEST_URL']
    url = _add_fields_to_url(url)
    headers = {'Authorization': 'Bearer {}'.format(app.config['AIRTABLE_API_KEY'])}
    params = app.config['REQUEST_PARAMS']

    # Make request and retrieve records in json format
    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    # Try to get records from data if the request was successful
    try:
        # If offset was included in data, retrieve additional paginated records
        if 'offset' in list(data.keys()):
            request_info = [url, headers, params]
            records = _get_paginated_records(data, request_info)
        else:
            records = data['records']
        formatted_records = _get_formatted_json_records(records)
        return formatted_records

    # If request was not successful, there will be no records field in response
    # Just return what is in cached layer and log an error
    except KeyError as e:
        body = "Results were not successfully retrieved from Airtable API. Please check connection parameters in config.py and fields in airtable_fields_config.json."
        logger.error(body)
        logger.error(f"Error Info: {e}")
        logger.error(f"API Response Info: {data}")

        # Configure the full email body
        body = "Hello Data Team,\n\n" + body
        body += f"\n\nError Info: {e}"

        try:
            body += f"\nType: {data['error']['type']}"  # If logging severity changes, this needs to be updated accordingly
            body += f"\nMessage: {data['error']['message']}"
        except KeyError:
            body += f"\nAPI Response Info: {data}"

        body += "\n\nSincerely,\nIIT Backend Alerts"

        with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
            server.login(sender, password)

            msg = MIMEText(body)
            msg['Subject'] = "ALERT: Unsuccessful Record Retrieval"
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)
            server.sendmail(sender, recipients, msg.as_string())

        records = read_from_json()
        return records


def write_to_json(records):
    with open('cached_results.json', 'w') as file:
        json.dump(records, file)
    return


def read_from_json():
    with open('cached_results.json', 'r') as file:
        records = json.load(file)
    return records
