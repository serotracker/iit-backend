from marshmallow import Schema, fields


class RecordDetailsSchema(Schema):
    source_id = fields.UUID(required=True)

