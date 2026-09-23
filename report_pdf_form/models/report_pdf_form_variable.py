# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo import fields, models


class ReportPDFFormVariable(models.Model):
    _name = "report.pdf.form.variable"
    _description = "Reusable variable to be evaluated in form fields code"

    report_form_id = fields.Many2one(
        "report.pdf.form", required=True, ondelete="cascade"
    )
    name = fields.Char()
    code = fields.Char()
