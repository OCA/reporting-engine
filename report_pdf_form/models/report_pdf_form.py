# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
import base64
import io

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.pdf import PdfFileWriter


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
    model_id = fields.Many2one("ir.model", ondelete="cascade", required=True)
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

    def action_preview_pdf(self):
        """Preview the PDF form with sample data."""
        self.ensure_one()

        if not self.pdf_attachment_id:
            raise UserError(self.env._("No PDF template attached to this form."))

        # Get a sample record of the model
        model_name = self.model_id.model
        sample_record = self.env[model_name].search([], limit=1)
        if not sample_record:
            message = self.env._(
                "No records found for model {model}. Cannot generate preview."
            ).format(model=model_name)
            raise UserError(message)

        # Generate the PDF using the same logic as the report
        try:
            # Decode the PDF attachment
            decoded_pdf = base64.b64decode(self.pdf_attachment_id.datas)

            # Create a PDF writer
            writer = PdfFileWriter()

            # Add pages from the template
            self.env["ir.actions.report"]._add_pages_to_writer_pdf(
                writer, decoded_pdf, f"template_{self.id}__"
            )

            # Prepare form fields mapping with sample values
            form_fields_values_mapping = {}
            for form_field in self.field_mapping_ids:
                if form_field.odoo_field_evaluation == "dotted_path":
                    try:
                        field_value = self.env[
                            "ir.actions.report"
                        ]._get_pdf_value_from_path(form_field, sample_record)
                    except Exception:
                        field_value = (
                            f"[ERROR: Invalid path {form_field.odoo_field_value}]"
                        )
                elif form_field.odoo_field_evaluation == "text":
                    field_value = form_field.odoo_field_value
                elif form_field.odoo_field_evaluation == "code":
                    try:
                        field_value = self.env[
                            "ir.actions.report"
                        ]._get_pdf_value_from_code(form_field, sample_record)
                    except Exception:
                        field_value = "[ERROR: Invalid code]"
                elif form_field.odoo_field_evaluation == "repeat_field":
                    continue
                else:
                    field_value = ""

                form_fields_values_mapping[
                    f"template_{self.id}__{form_field.pdf_field_name}"
                ] = field_value

            # Fill the form fields
            from odoo.tools import pdf

            pdf.fill_form_fields_pdf(writer, form_fields=form_fields_values_mapping)

            # Save to bytes
            with io.BytesIO() as buffer:
                writer.write(buffer)
                pdf_content = buffer.getvalue()

            # Create an attachment with the preview
            attachment = self.env["ir.attachment"].create(
                {
                    "name": f"preview_{self.name}.pdf",
                    "type": "binary",
                    "datas": base64.b64encode(pdf_content),
                    "mimetype": "application/pdf",
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )

            # Return action to open the preview
            return {
                "type": "ir.actions.act_url",
                "url": f"/web/content/{attachment.id}/{attachment.name}",
                "target": "new",
            }
        except Exception as e:
            message = self.env._("Could not generate PDF preview: {error}").format(
                error=str(e)
            )
            raise UserError(message) from e
