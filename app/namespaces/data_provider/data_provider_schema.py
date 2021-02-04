from marshmallow import Schema, fields, validate
from app.serotracker_sqlalchemy.db_model_config import all_cols
from app.utils.filter_option_utils import all_filter_types


class RecordsSchema(Schema):
    sorting_key = fields.String(validate=validate.OneOf(["serum_pos_prevalence", "denominator_value",
                                                         "overall_risk_of_bias", "source_name",
                                                         "source_id"]))
    page_index = fields.Integer(allow_none=True)
    per_page = fields.Integer(allow_none=True)
    reverse = fields.Boolean(allow_none=True)
    research_fields = fields.Boolean(allow_none=True)
    prioritize_estimates = fields.Boolean(allow_none=True)
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(all_filter_types)),
        values=fields.List(fields.String())
    )
    columns = fields.List(fields.String(validate=validate.OneOf(all_cols)))
    # Date fields should be supplied as unix timestamp
    start_date = fields.String()
    end_date = fields.String()


class RecordDetailsSchema(Schema):
    source_id = fields.UUID(required=True)
    start_date = fields.String()
    end_date = fields.String()


class StudyCountSchema(Schema):
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(all_filter_types)),
        values=fields.List(fields.String())
    )
    start_date = fields.String()
    end_date = fields.String()

