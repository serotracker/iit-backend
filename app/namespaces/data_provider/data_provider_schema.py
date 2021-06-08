from marshmallow import Schema, fields, validate


class RecordsSchema(Schema):
    sorting_key = fields.String(validate=validate.OneOf(["serum_pos_prevalence", "denominator_value",
                                                         "overall_risk_of_bias", "source_name",
                                                         "source_id", "sampling_end_date"]))
    # TODO: Deprecate page_index, sorting_key, per_page, reverse from RecordsSchema once we update the frontend to not make requests to /records
    page_index = fields.Integer(allow_none=True)
    per_page = fields.Integer(allow_none=True)
    reverse = fields.Boolean(allow_none=True)
    research_fields = fields.Boolean(allow_none=True)
    prioritize_estimates = fields.Boolean(allow_none=True)
    prioritize_estimates_mode = fields.String(validate=validate.OneOf(['analysis_dynamic',
                                                                       'analysis_static',
                                                                       'dashboard']), allow_none=True)
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(["country", "source_type", "overall_risk_of_bias",
                                                    "source_name", "population_group", "genpop",
                                                    "sex", "age", "isotypes_reported", "test_type",
                                                    "specimen_type", "estimate_grade",
                                                    "subgroup_var", "subgroup_cat",
                                                    "state", "city", "antibody_target"])),
        values=fields.List(fields.String())
    )
    columns = fields.List(fields.String(validate=validate.OneOf(["age", "city", "state", "population_group",
                                                                 "test_manufacturer", "approving_regulator",
                                                                 "test_type", "specimen_type", "source_id",
                                                                 "source_name", "publication_date", "first_author",
                                                                 "url", "source_type", "source_publisher",
                                                                 "summary", "study_type", "country",
                                                                 "lead_organization", "sampling_start_date",
                                                                 "sampling_end_date", "sex", "sampling_method",
                                                                 "sensitivity", "specificity", "included",
                                                                 "denominator_value", "numerator_definition",
                                                                 "serum_pos_prevalence", "overall_risk_of_bias",
                                                                 "estimate_grade", "isotypes_reported", "created_at",
                                                                 "pin_longitude", "pin_latitude", "pin_region_type",
                                                                 "is_unity_aligned", "antibody_target"])))
    # Date fields should be supplied as unix timestamp
    sampling_start_date = fields.String()
    sampling_end_date = fields.String()
    publication_start_date = fields.String()
    publication_end_date = fields.String()
    include_in_srma = fields.Boolean(allow_none=True)
    include_disputed_regions = fields.Boolean(allow_none=True)
    include_subgeography_estimates = fields.Boolean(allow_none=True)
    unity_aligned = fields.Boolean(allow_none=True)


class PaginatedRecordsSchema(RecordsSchema):
    sorting_key = fields.String(validate=validate.OneOf(["serum_pos_prevalence", "denominator_value",
                                                         "overall_risk_of_bias", "source_name",
                                                         "source_id", "sampling_end_date"]), allow_none=True)
    min_page_index = fields.Integer(required=True)
    max_page_index = fields.Integer(required=True)
    per_page = fields.Integer(allow_none=True)
    reverse = fields.Boolean(allow_none=True)


class RecordDetailsSchema(Schema):
    source_id = fields.UUID(required=True)
    sampling_start_date = fields.String()
    sampling_end_date = fields.String()


class StudyCountSchema(Schema):
    filters = fields.Dict(
        keys=fields.String(validate=validate.OneOf(["country", "source_type", "overall_risk_of_bias",
                                                    "source_name", "population_group", "genpop",
                                                    "sex", "age", "isotypes_reported", "test_type",
                                                    "specimen_type", "estimate_grade",
                                                    "subgroup_var", "subgroup_cat",
                                                    "state", "city", "antibody_target"])),
        values=fields.List(fields.String())
    )
    sampling_start_date = fields.String()
    sampling_end_date = fields.String()
    unity_aligned = fields.Boolean(allow_none=True)
