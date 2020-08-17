from marshmallow import Schema, fields, validate


class RecordsSchema(Schema):
    sorting_key = fields.String(validate=validate.OneOf(["serum_pos_prevalence", "denominator_value",
                                                         "overall_risk_of_bias", "source_name",
                                                         "source_id"]))
    page_index = fields.Integer()
    per_page = fields.Integer()
    reverse = fields.Boolean()
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(["country", "source_type", "overall_risk_of_bias",
                                                    "study_status", "source_name", "population_group",
                                                    "sex", "age", "isotypes_reported", "test_type",
                                                    "specimen_type", "estimate_grade"])),
        values=fields.List(fields.String())
    )
    columns = fields.List(fields.String())
    # Date fields should be supplied as unix timestamp
    start_date = fields.Integer()
    end_date = fields.Integer()


class RecordDetailsSchema(Schema):
    source_id = fields.UUID(required=True)


class StudyCountSchema(Schema):
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(["country"])),
        values=fields.List(fields.String())
    )
