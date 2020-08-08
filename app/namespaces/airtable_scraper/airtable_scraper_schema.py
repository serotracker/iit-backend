from marshmallow import Schema, fields


class StudyCountSchema(Schema):
    records = fields.List(fields.Dict, required=True)

