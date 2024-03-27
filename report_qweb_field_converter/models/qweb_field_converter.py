# Copyright 2024 Quartile Limited (https://www.quartile.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QwebFieldConverter(models.Model):
    _name = "qweb.field.converter"
    _description = "Qweb Field Converter"
    _order = "res_model_id, field_id"

    res_model_id = fields.Many2one(
        "ir.model", string="Model", ondelete="cascade", required=True
    )
    res_model_name = fields.Char("Model Name", related="res_model_id.model", store=True)
    field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id', '=', res_model_id)]",
        string="Field",
        ondelete="cascade",
        required=True,
    )
    field_type = fields.Selection(related="field_id.ttype", store=True)
    field_name = fields.Char("Field Name", related="field_id.name", store=True)
    uom_id = fields.Many2one("uom.uom", string="UoM", ondelete="cascade")
    uom_field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id', '=', res_model_id), ('relation', '=', 'uom.uom')]",
        string="UoM Field",
        ondelete="cascade",
    )
    currency_id = fields.Many2one("res.currency", string="Currency", ondelete="cascade")
    currency_field_id = fields.Many2one(
        "ir.model.fields",
        domain="[('model_id', '=', res_model_id), ('relation', '=', 'res.currency')]",
        string="Currency Field",
        ondelete="cascade",
    )
    field_options = fields.Text(
        "Options", help="JSON-formatted string to specify field formatting options"
    )
    digits = fields.Integer()
    company_id = fields.Many2one("res.company", string="Company")

    def _get_score(self, record):
        self.ensure_one()
        score = 1
        if self.company_id:
            if record.company_id == self.company_id:
                score += 1
            else:
                return -1
        if self.uom_id:
            if record[self.uom_field_id.sudo().name] == self.uom_id:
                score += 1
            else:
                return -1
        if self.currency_id:
            if record[self.currency_field_id.sudo().name] == self.currency_id:
                score += 1
            else:
                return -1
        return score
