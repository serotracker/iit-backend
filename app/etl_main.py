import requests
import json
import os
import logging
from uuid import uuid4

import pandas as pd

logger = logging.getLogger(__name__)

AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_REQUEST_URL = "https://api.airtable.com/v0/{}/Rapid%20Review%3A%20Estimates?".format(AIRTABLE_BASE_ID)
AIRTABLE_REQUEST_PARAMS = {'filterByFormula': '{Visualize on SeroTracker?}=1'}


def _add_fields_to_url(url):
    # Add fields in config to api URL
    with open('utils/airtable_fields_config.json', 'r') as file:
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
    with open('utils/airtable_fields_config.json', 'r') as file:
        fields = json.load(file)
        renamed_cols = {key: fields[key] for key in fields}
        reordered_cols = [fields[key] for key in fields]
    total_records_df = total_records_df.rename(columns=renamed_cols)
    total_records_df = total_records_df[reordered_cols]
    total_records_df = total_records_df.where(total_records_df.notna(), None)
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


def get_all_records():
    # Get airtable API URL and add fields to be scraped to URL in HTML format
    url = AIRTABLE_REQUEST_URL.format(AIRTABLE_BASE_ID)
    url = _add_fields_to_url(url)
    headers = {'Authorization': 'Bearer {}'.format(AIRTABLE_API_KEY)}
    params = AIRTABLE_REQUEST_PARAMS

    # Make request and retrieve records in json format
    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    # Try to get records from data if the request was successful
    try:
        # If offset was included in data, retrieve additional paginated records
        if 'offset' in list(data.keys()):
            parameters = params.copy()
            request_info = [url, headers, parameters]
            records = _get_paginated_records(data, request_info)
        else:
            records = data['records']
        formatted_records = _get_formatted_json_records(records)
        return formatted_records

    # If request was not successful, there will be no records field in response
    # Just return what is in cached layer and log an error
    except KeyError as e:
        body = "Results were not successfully retrieved from Airtable API." \
               "Please check connection parameters in config.py and fields in airtable_fields_config.json."
        logger.error(body)
        logger.error(f"Error Info: {e}")
        logger.error(f"API Response Info: {data}")

        request_info = {
            "url": url,
            "headers": json.dumps(headers)
        }
        return request_info


def main():
    json = get_all_records()
    data = pd.DataFrame(json)

    single_select_cols = ['SOURCE_NAME', 'PUBLICATION_DATE', 'FIRST_AUTHOR', 'URL', 'SOURCE_TYPE', 'SUMMARY',
                          'STUDY_TYPE', 'STUDY_STATUS', 'COUNTRY', 'LEAD_ORGANIZATION', 'SAMPLING_START', 'SAMPLING_END',
                          'OVERALL_RISK_OF_BIAS']

    # Remove lists from single select columns
    for col in single_select_cols:
        data[col] = data[col].apply(lambda x: x[0] if x is not None else x)

    # Create airtable source df
    # Drop columns not needed
    airtable_source = data.drop(columns=['CITY', 'STATE', 'AGE', 'SOURCE_PUBLISHER', 'POPULATION_GROUP',
                                         'TEST_MANUFACTURER', 'APPROVING_REGULATOR', 'TEST_TYPE', 'SPECIMEN_TYPE'])

    # Length of records
    num_records = airtable_source.shape[0]

    ## ISSUE: THE SAME PREVALENCE IS RECORDED BY MULTIPLE SOURCES, THEREFORE EVERY COLUMN CAN TECHNICALLY HAVE MULTIPLE VALUES.
    ## SHOULD WE INCLUDE ALL THE SOURCES OF THE ESTIMATE, OR JUST TAKE ONE OF THEM?
    return


if __name__ == '__main__':
    main()
