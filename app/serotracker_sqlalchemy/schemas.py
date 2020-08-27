from marshmallow import Schema, fields, validate

class AirtableSourceSchema(Schema):
    source_id = fields.UUID()
    source_name = fields.Str()
    #publication_date = fields.DateTime()
    first_author = fields.Str(validate=validate.Length(max=128))
    url = fields.Str()
    source_type = fields.Str(validate=validate.Length(max=64))
    source_publisher = fields.Str(validate=validate.Length(max=256))
    summary = fields.Str()
    study_type = fields.Str(validate=validate.Length(max=128))
    study_status = fields.Str(validate=validate.Length(max=32))
    country = fields.Str(validate=validate.Length(max=64))
    lead_organization = fields.Str(validate=validate.Length(max=128))
    #sampling_start_date = fields.DateTime()
    #sampling_end_date = fields.DateTime()
    sex = fields.Str(validate=validate.Length(max=16))
    sampling_method = fields.Str(validate=validate.Length(max=128))
    sensitivity = fields.Float()
    specificity = fields.Float()
    include_in_n = fields.Boolean()
    denominator_value = fields.Integer()
    numerator_definition = fields.Str()
    serum_pos_prevalence = fields.Float()
    overall_risk_of_bias = fields.Str(validate=validate.Length(max=128))
    isotype_igg = fields.Boolean()
    isotype_igm = fields.Boolean()
    isotype_iga = fields.Boolean()
    estimate_grade = fields.Str(validate=validate.Length(max=32))
    #created_at = fields.DateTime()

# Multi select table schemas
class CitySchema(Schema):
    city_id = fields.UUID()
    city_name = fields.Str(validate=validate.Length(max=128))
    # created_at = fields.DateTime()

class StateSchema(Schema):
    state_id = fields.UUID()
    state_name = fields.Str(validate=validate.Length(max=128))
    # created_at = fields.DateTime()

class AgeSchema(Schema):
    age_id = fields.UUID()
    age_name = fields.Str(validate=validate.Length(max=64))
    # created_at = fields.DateTime()


class PopulationGroupSchema(Schema):
    population_group_id = fields.UUID()
    population_group_name = fields.Str(validate=validate.Length(max=128))
    # created_at = fields.DateTime()


class TestManufacturerSchema(Schema):
    test_manufacturer_id = fields.UUID()
    test_manufacturer_name = fields.Str(validate=validate.Length(max=128))
    #created_at = fields.DateTime()


class ApprovingRegulatorSchema(Schema):
    approving_regulator_id = fields.UUID()
    approving_regulator_name = fields.Str(validate=validate.Length(max=256))
    # created_at = fields.DateTime()


class TestTypeSchema(Schema):
    test_type_id = fields.UUID()
    test_type_name = fields.Str(validate=validate.Length(max=256))
    # created_at = fields.DateTime()


class SpecimenTypeSchema(Schema):
    specimen_type_id = fields.UUID()
    specimen_type_name = fields.Str(validate=validate.Length(max=64))
    # created_at = fields.DateTime()
