import logging

import requests

from flask import current_app as app
from app.utils import read_from_json, send_api_error_slack_notif

logger = logging.getLogger(__name__)


def get_all_records():
    # Get URL for API request
    url = app.config['JHU_REQUEST_URL']

    # Make request and retrieve records in json format
    r = requests.get(url)
    data = r.json()
    logging.info(data)
    status_code = r.status_code
    logging.info(status_code)

    # If status code is not 200, send error emails and read records in cached json layer
    if status_code != 200:
        # Log error and send error email
        body = "Results were not successfully retrieved from JHU API. " \
               "Request returned status code {}.".format(status_code)
        logger.info(body)
        logger.info(f"API Response Info: {data}")

        request_info = {
            "url": url,
            "headers": None
        }
        send_api_error_slack_notif(body, data, request_info=request_info)

        # Read and return data from cached json
        data = read_from_json(app.config['JHU_CACHED_RESULTS_PATH'])
    return data, status_code
