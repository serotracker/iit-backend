from marshmallow import Schema, fields


class TestAdjustmentSchema(Schema):
    test_adj = fields.String(required=True)
    ind_se = fields.String(required=True)
    ind_sp = fields.String(required=True)
    ind_se_n = fields.String(required=True)
    ind_sp_n = fields.String(required=True)
    se_n = fields.String(required=True)
    sp_n = fields.String(required=True)
    sensitivity = fields.String(required=True)
    specificity = fields.String(required=True)
    test_validation = fields.String(required=True)
    test_type = fields.String(required=True)
    denominator_value = fields.String(required=True)
    serum_pos_prevalence = fields.String(required=True)
