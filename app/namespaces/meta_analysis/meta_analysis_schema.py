from marshmallow import Schema, fields, validate


class MetaSchema(Schema):
    class StudyCountSchema(Schema):
        filters = fields.Dict(
            keys=fields.String(validate=validate.OneOf(["country"])),
            values=fields.List(fields.String())
        )
    aggregation_variable = fields.String()
    meta_analysis_transformation = fields.String()
    meta_analysis_technique = fields.String()

