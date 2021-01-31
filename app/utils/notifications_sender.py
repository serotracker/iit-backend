import os
import logging

from slack_sdk import WebClient


def send_api_error_slack_notif(body, data, error=None, request_info=None, channel='#dev-logging-data'):
    # Log errors and info
    logging.error(body)
    logging.error(f"Error Info: {error}")
    logging.error(f"API Response Info: {data}")

    # Add error to response body if exists
    if error is not None:
        body += f"\n\nError Info: {error}"

    try:
        body += f"\nType: {data['error']['type']}"
        body += f"\nMessage: {data['error']['message']}"
    except (KeyError, TypeError):
        body += f"\nAPI Response Info: {data}"

    if request_info is not None:
        body += f"\n\nAPI Request info"
        body += f"\nURL: {request_info['url']}"
        body += f"\nHeaders: {request_info['headers']}"
    send_slack_message(body, channel=channel)
    return


def send_schema_validation_slack_notif(unacceptable_records_map):
    # Configure the slack notification body
    body = "Hello Data Team,\n\nThere were one or more records " \
           "that did not meet the schema criteria, as follows:\n\n"

    for record, errors in unacceptable_records_map.items():
        body += f"Record: {record}\n"
        body += f"Errors: {errors}\n\n"

    body += "\nSincerely,\nIIT Backend Alerts"
    send_slack_message(body, channel='#dev-logging-etl')
    return


def send_slack_message(message, channel='#dev-logging-backend'):
    bot_token = os.getenv('SLACKBOT_TOKEN')
    client = WebClient(bot_token)
    client.chat_postMessage(channel=channel, text=message)
    return
