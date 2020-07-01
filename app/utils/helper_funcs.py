from marshmallow import ValidationError


def validate_request_input_against_schema(input_payload, schema):
    try:
        payload = schema.load(input_payload)
    except ValidationError as err:
        return err.messages, 422
    return payload, 200
