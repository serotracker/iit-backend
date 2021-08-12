from marshmallow import Schema, fields


class TestAdjustmentSchema(Schema):
    test_adj = fields.Boolean(allow_none=True)
    ind_se = fields.Float(allow_none=True)
    ind_sp = fields.Float(allow_none=True)
    ind_se_n = fields.Integer(allow_none=True)
    ind_sp_n = fields.Integer(allow_none=True)
    se_n = fields.Integer(allow_none=True)
    sp_n = fields.Integer(allow_none=True)
    sensitivity = fields.Float(allow_none=True)
    specificity = fields.Float(allow_none=True)
    test_validation = fields.String(allow_none=True)
    test_type = fields.String(allow_none=True)
    denominator_value = fields.Integer(allow_none=True)
    serum_pos_prevalence = fields.Float(allow_none=True)
