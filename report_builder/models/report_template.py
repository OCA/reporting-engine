# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReportTemplate(models.Model):
    _name = "report.template"
    _description = "Template"

    name = fields.Char(required=True)
    source = fields.Selection(
        selection=lambda self: self.env["report.template.kpi.query.kind"]
        ._fields["source"]
        .selection,
        required=True,
        default="account",
    )
    kpi_ids = fields.One2many(
        "report.template.kpi",
        "template_id",
    )
    search_view_id = fields.Many2one(
        "ir.ui.view",
        domain="[('type', '=', 'search'), ('model', '=', search_model)]",
    )
    search_model_id = fields.Many2one("ir.model")
    search_model = fields.Char(related="search_model_id.model")
    style_id = fields.Many2one("report.style")
