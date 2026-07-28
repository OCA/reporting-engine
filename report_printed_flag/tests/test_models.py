from odoo import fields, models


class TestPrintedModel(models.Model):
    _name = "test.printed.model"
    _inherit = ["report.printed.mixin"]
    _description = "Test Printed Model"

    name = fields.Char()
    company_id = fields.Many2one("res.company")
    # 'printed' field comes from report.printed.mixin


class TestPrintedNoNameModel(models.Model):
    _name = "test.printed.noname.model"
    _inherit = ["report.printed.mixin"]
    _description = "Test Printed Model Without Name"

    value = fields.Char()
    company_id = fields.Many2one("res.company", required=True)
    # 'printed' field comes from report.printed.mixin
