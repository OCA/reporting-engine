# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo import fields, models


class ReportPDFFormField(models.Model):
    _name = "report.pdf.form.field"
    _description = "Mapping of Odoo field to PDF form field"

    report_form_id = fields.Many2one(
        "report.pdf.form", required=True, ondelete="cascade"
    )
    pdf_field_name = fields.Char(string="PDF Form Field Name", required=True)
    odoo_field_evaluation = fields.Selection(
        [
            ("dotted_path", "Dotted field path"),
            ("text", "Static text"),
            ("code", "Python code"),
            ("repeat_field", "Repeat field"),
        ],
        required=True,
        default="dotted_path",
    )
    odoo_field_value = fields.Char(
        help="Dot-separated path to field from the record, e.g. partner_id.name, "
        "or python code",
        required=True,
    )
