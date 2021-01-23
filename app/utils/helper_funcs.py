import os

from datetime import datetime

from marshmallow import ValidationError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def validate_request_input_against_schema(input_payload, schema):
    try:
        payload = schema.load(input_payload)
    except ValidationError as err:
        return err.messages, 422
    return payload, 200


def convert_start_end_dates(data):
    start_date = data.get('start_date')
    if start_date:
        # Python's datetime module does not
        # support ISO 8601 strings whose UTC offsets = Z (aka GMT or UK time)
        # see https://stackoverflow.com/questions/127803/how-do-i-parse-an-iso-8601-formatted-date
        start_date = start_date.replace("Z", "+00:00")
        start_date = datetime.fromisoformat(start_date).replace(tzinfo=None)
    end_date = data.get('end_date')
    if end_date:
        end_date = end_date.replace("Z", "+00:00")
        end_date = datetime.fromisoformat(end_date).replace(tzinfo=None)
    return start_date, end_date


def send_slack_message(channel, message):
    print(channel, message)
    token = os.getenv("SLACK_BOT_TOKEN")
    print(token)
    client = WebClient(token)
    response = client.chat_postMessage(channel=channel, text='@channel Internal Server Error: {}'.format(message))
    print(response)
    return
