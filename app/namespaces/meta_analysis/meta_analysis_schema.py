from marshmallow import Schema, fields, validate
from app.utils.filter_option_utils import all_filter_types


class MetaSchema(Schema):
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(all_filter_types)),
        values=fields.List(fields.String())
    )
    aggregation_variable = fields.String()
    meta_analysis_transformation = fields.String()
    meta_analysis_technique = fields.String()
    start_date = fields.String()
    end_date = fields.String()
