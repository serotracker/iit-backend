from datetime import datetime

from marshmallow import ValidationError


def validate_request_input_against_schema(input_payload, schema):
    try:
        payload = schema.load(input_payload)
    except ValidationError as err:
        return err.messages, 422
    return payload, 200


def convert_start_end_dates(data):
    start_date = data.get('start_date')
    if start_date:
        start_date = datetime.utcfromtimestamp(start_date)
    end_date = data.get('end_date')
    if end_date:
        end_date = datetime.utcfromtimestamp(end_date)
    return start_date, end_date
