from marshmallow import Schema, fields, validate


class RecordsSchema(Schema):
    sorting_key = fields.String(validate=validate.OneOf(["serum_pos_prevalence", "denominator_value",
                                                         "overall_risk_of_bias", "source_name"]))
    page_index = fields.Integer()
    per_page = fields.Integer()
    reverse = fields.Boolean()
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(["country", "source_type", "overall_risk_of_bias",
                                                    "study_status", "source_name", "population_group_name",
                                                    "sex", "age_name", "isotypes_reported", "test_type_name",
                                                    "specimen_type_name", "estimate_grade"])),
        values=fields.List(fields.String())
    )
    # Date fields should be supplied as unix timestamp
    start_date = fields.Integer()
    end_date = fields.Integer()


class RecordDetailsSchema(Schema):
    source_id = fields.UUID(required=True)

