from marshmallow import Schema, fields, validate


class RecordsSchema(Schema):
    sorting_key = fields.String(validate=validate.OneOf(["serum_pos_prevalence", "denominator_value",
                                                         "overall_risk_of_bias", "source_name",
                                                         "source_id"]))
    page_index = fields.Integer(allow_none=True)
    per_page = fields.Integer(allow_none=True)
    reverse = fields.Boolean(allow_none=True)
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(["country", "source_type", "overall_risk_of_bias",
                                                    "study_status", "source_name", "population_group",
                                                    "sex", "age", "isotypes_reported", "test_type",
                                                    "specimen_type", "estimate_grade"])),
        values=fields.List(fields.String())
    )
    columns = fields.List(fields.String(validate=validate.OneOf(["age", "city", "state", "population_group",
                                                                 "test_manufacturer", "approving_regulator",
                                                                 "test_type", "specimen_type", "source_id",
                                                                 "source_name", "publication_date", "first_author",
                                                                 "url", "source_type", "source_publisher",
                                                                 "summary", "study_type", "study_status", "country",
                                                                 "lead_organization", "sampling_start_date",
                                                                 "sampling_end_date", "sex", "sampling_method",
                                                                 "sensitivity", "specificity", "include_in_n",
                                                                 "denominator_value", "numerator_definition",
                                                                 "serum_pos_prevalence", "overall_risk_of_bias",
                                                                 "estimate_grade", "isotypes_reported", "created_at"])))
    # Date fields should be supplied as unix timestamp
    start_date = fields.String()
    end_date = fields.String()


class RecordDetailsSchema(Schema):
    source_id = fields.UUID(required=True)
    start_date = fields.String()
    end_date = fields.String()


class StudyCountSchema(Schema):
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(["country", "source_type", "overall_risk_of_bias",
                                                    "study_status", "source_name", "population_group",
                                                    "sex", "age", "isotypes_reported", "test_type",
                                                    "specimen_type", "estimate_grade"])),
        values=fields.List(fields.String())
    )
    start_date = fields.String()
    end_date = fields.String()

