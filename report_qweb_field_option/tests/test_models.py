# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class TestQwebFieldModel(models.Model):
    _name = "test.qweb.field.options"
    _description = "Test Qweb Field Options"

    name = fields.Char()
    quantity = fields.Float()
    uom_id = fields.Many2one("uom.uom")
    value = fields.Float(string="Rounding Factor")
    currency_id = fields.Many2one("res.currency")
    company_id = fields.Many2one("res.company")
