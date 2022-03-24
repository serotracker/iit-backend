from marshmallow import Schema, fields, validate


class DashboardSourceSchema(Schema):
    source_id = fields.UUID(allow_none=True)
    source_name = fields.Str(allow_none=True)
    first_author = fields.Str(validate=validate.Length(max=128), allow_none=True)
    url = fields.Str(allow_none=True)
    source_type = fields.Str(validate=validate.Length(max=64), allow_none=True)
    source_publisher = fields.Str(validate=validate.Length(max=256), allow_none=True)
    summary = fields.Str(allow_none=True)
    study_name = fields.Str(allow_none=True)
    study_type = fields.Str(validate=validate.Length(max=128), allow_none=True)
    study_status = fields.Str(validate=validate.Length(max=32), allow_none=True)
    country = fields.Str(validate=validate.Length(max=64), allow_none=True)
    lead_organization = fields.Str(validate=validate.Length(max=128), allow_none=True)
    sex = fields.Str(validate=validate.Length(max=16), allow_none=True)
    age = fields.Str(validate=validate.Length(max=64), allow_none=True)
    population_group = fields.Str(validate=validate.Length(max=128), allow_none=True)
    sampling_method = fields.Str(validate=validate.Length(max=128), allow_none=True)
    sensitivity = fields.Float(allow_none=True, allow_nan=True)
    specificity = fields.Float(allow_none=True, allow_nan=True)
    included = fields.Boolean(allow_none=True)
    # Should be an int but doing this so that we can guard against NaN values
    denominator_value = fields.Float(allow_none=True, allow_nan=True)
    numerator_definition = fields.Str(allow_none=True)
    serum_pos_prevalence = fields.Float(allow_none=True, allow_nan=True)
    overall_risk_of_bias = fields.Str(validate=validate.Length(max=128), allow_none=True)
    isotype_igg = fields.Boolean(allow_none=True)
    isotype_igm = fields.Boolean(allow_none=True)
    isotype_iga = fields.Boolean(allow_none=True)
    specimen_type = fields.Str(validate=validate.Length(max=64), allow_none=True)
    estimate_grade = fields.Str(validate=validate.Length(max=32), allow_none=True)
    city = fields.List(fields.Str(validate=validate.Length(max=128)), allow_none=True)
    state = fields.List(fields.Str(validate=validate.Length(max=128)), allow_none=True)
    test_manufacturer = fields.List(fields.Str(validate=validate.Length(max=128)), allow_none=True)
    academic_primary_estimate = fields.Boolean(allow_none=True)
    dashboard_primary_estimate = fields.Boolean(allow_none=True)
    test_adj = fields.Boolean(allow_none=True)
    pop_adj = fields.Boolean(allow_none=True)
    isotype_comb = fields.Str(validate=validate.Length(max=32), allow_none=True)
    test_type = fields.Str(validate=validate.Length(max=256), allow_none=True)


class ResearchSourceSchema(Schema):
    source_id = fields.UUID(allow_none=True)
    case_population = fields.Float(allow_none=True, allow_nan=True)
    deaths_population = fields.Float(allow_none=True, allow_nan=True)
    age_max = fields.Float(allow_none=True, allow_nan=True)
    age_min = fields.Float(allow_none=True, allow_nan=True)
    age_variation = fields.Str(allow_none=True)
    age_variation_measure = fields.Str(allow_none=True)
    average_age = fields.Str(allow_none=True)
    case_count_neg14 = fields.Float(allow_none=True, allow_nan=True)
    case_count_neg9 = fields.Float(allow_none=True, allow_nan=True)
    case_count_0 = fields.Float(allow_none=True, allow_nan=True)
    death_count_plus11 = fields.Float(allow_none=True, allow_nan=True)
    death_count_plus4 = fields.Float(allow_none=True, allow_nan=True)
    include_in_srma = fields.Boolean(allow_none=True)
    sensspec_from_manufacturer = fields.Boolean(allow_none=True)
    ind_eval_lab = fields.Str(allow_none=True)
    ind_eval_link = fields.Str(allow_none=True)
    ind_se = fields.Float(allow_none=True, allow_nan=True)
    ind_se_n = fields.Float(allow_none=True, allow_nan=True)
    ind_sp = fields.Float(allow_none=True, allow_nan=True)
    ind_sp_n = fields.Float(allow_none=True, allow_nan=True)
    jbi_1 = fields.Str(allow_none=True)
    jbi_2 = fields.Str(allow_none=True)
    jbi_3 = fields.Str(allow_none=True)
    jbi_4 = fields.Str(allow_none=True)
    jbi_5 = fields.Str(allow_none=True)
    jbi_6 = fields.Str(allow_none=True)
    jbi_7 = fields.Str(allow_none=True)
    jbi_8 = fields.Str(allow_none=True)
    jbi_9 = fields.Str(allow_none=True)
    measure_of_age = fields.Str(allow_none=True)
    sample_frame_info = fields.Str(allow_none=True)
    number_of_females = fields.Float(allow_none=True, allow_nan=True)
    number_of_males = fields.Float(allow_none=True, allow_nan=True)
    numerator_value = fields.Float(allow_none=True, allow_nan=True)
    estimate_name = fields.Str(allow_none=True)
    test_not_linked_reason = fields.Str(allow_none=True)
    se_n = fields.Float(allow_none=True, allow_nan=True)
    seroprev_95_ci_lower = fields.Float(allow_none=True, allow_nan=True)
    seroprev_95_ci_upper = fields.Float(allow_none=True, allow_nan=True)
    sp_n = fields.Float(allow_none=True, allow_nan=True)
    subgroup_var = fields.Str(allow_none=True)
    subgroup_cat = fields.Str(allow_none=True)
    superceded = fields.Boolean(allow_none=True)
    test_linked_uid = fields.Str(allow_none=True)
    test_name = fields.Str(allow_none=True)
    test_validation = fields.Str(allow_none=True)
    zotero_citation_key = fields.Str(allow_none=True)
    superseder_name = fields.Str(allow_none=True)
    study_exclusion_criteria = fields.Str(allow_none=True)

