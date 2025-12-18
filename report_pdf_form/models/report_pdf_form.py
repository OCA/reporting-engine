# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ReportPDFForm(models.Model):
    _name = "report.pdf.form"
    _description = "PDF Form Report Template"
    _inherits = {
        "ir.actions.report": "report_id",
    }

    def write(self, vals):
        # Ensure report_id is unique by checking before write
        if "report_id" in vals:
            existing = self.search([("report_id", "=", vals["report_id"])])
            if len(existing) > 1:  # If there would be duplicates after update
                raise ValidationError(
                    self.env._("The report must be unique for a PDF form report.")
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "report_id" in vals:
                existing = self.search_count([("report_id", "=", vals["report_id"])])
                if existing > 0:
                    raise ValidationError(
                        self.env._("The report must be unique for a PDF form report.")
                    )
        return super().create(vals_list)

    # name = fields.Char(required=True, translate=True)
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
