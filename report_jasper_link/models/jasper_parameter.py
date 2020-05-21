# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class JasperParameter(models.Model):
    _name = "jasper.parameter"
    _description = "Jasper Parameter"

    name = fields.Char(
        string="Name",
        required=True,
    )
    value = fields.Char(
        string="Value",
        required=True,
    )
    report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Report",
    )