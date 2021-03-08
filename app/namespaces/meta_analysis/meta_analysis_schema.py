from marshmallow import Schema, fields, validate


class MetaSchema(Schema):
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(["country", "source_type", "overall_risk_of_bias",
                                                    "study_status", "source_name", "population_group",
                                                    "sex", "age", "isotypes_reported", "test_type",
                                                    "specimen_type", "estimate_grade"])),
        values=fields.List(fields.String())
    )
    aggregation_variable = fields.String()
    meta_analysis_transformation = fields.String()
    meta_analysis_technique = fields.String()
    sampling_start_date = fields.String()
    sampling_end_date = fields.String()
