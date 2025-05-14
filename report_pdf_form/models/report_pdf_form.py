# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo import fields, models


class ReportPDFForm(models.Model):
    _name = "report.pdf.form"
    _description = "PDF Form Report Template"
    _inherits = {
        "ir.actions.report": "report_id",
    }

    # name = fields.Char(required=True, translate=True)
    # TODO: Add constraint for unique ref
    # ref = fields.Char(required=True)
    pdf_attachment_id = fields.Many2one(
        string="Related attachment",
        comodel_name="ir.attachment",
        ondelete="cascade",
        required=True,
    )
    # TODO: Check if needed
    report_id = fields.Many2one(
        "ir.actions.report",
        ondelete="cascade",
        required=True,
    )
    # model_id = fields.Many2one("ir.model", ondelete="cascade", required=True)
    # TODO:
    field_mapping_ids = fields.One2many(
        "report.pdf.form.field",
        "report_form_id",
        required=True,
    )
    field_variable_ids = fields.One2many(
        "report.pdf.form.variable",
        "report_form_id",
    )
