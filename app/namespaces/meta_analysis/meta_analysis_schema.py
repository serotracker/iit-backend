from marshmallow import Schema, fields


class MetaSchema(Schema):
    records = fields.List(fields.Dict, required=True)
    aggregation_variable = fields.String(required=True)
    meta_analysis_transformation = fields.String()
    meta_analysis_technique = fields.String()
