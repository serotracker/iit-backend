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
        start_date = datetime.fromisoformat(start_date).replace(tzinfo=None)
    end_date = data.get('end_date')
    if end_date:
        end_date = datetime.fromisoformat(end_date).replace(tzinfo=None)
    return start_date, end_date
