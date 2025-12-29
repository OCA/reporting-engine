# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    is_valid = fields.Boolean(compute="_compute_is_valid", store=True, readonly=True)
    validation_message = fields.Char(
        compute="_compute_validation_message",
        store=True,
        readonly=True,
    )

    @api.depends("odoo_field_evaluation", "odoo_field_value", "report_form_id.model_id")
    def _compute_is_valid(self):
        for record in self:
            record.is_valid = record._validate_dotted_path()

    @api.depends("is_valid", "odoo_field_evaluation", "odoo_field_value")
    def _compute_validation_message(self):
        for record in self:
            if record.odoo_field_evaluation != "dotted_path":
                record.validation_message = "Validation not applicable"
            elif record.is_valid:
                record.validation_message = "Valid path"
            else:
                record.validation_message = f"Invalid path: {record.odoo_field_value}"

    def _validate_dotted_path(self):
        """Validate if the dotted path is valid for the model."""
        self.ensure_one()
        if self.odoo_field_evaluation != "dotted_path" or not self.odoo_field_value:
            return True  # Not a dotted path or empty, considered valid

        # Get the model from the parent report form
        model_name = self.report_form_id.model_id.model
        if not model_name:
            return False

        # Split the dotted path
        path_parts = self.odoo_field_value.split(".")

        # Start with the base model
        current_model = self.env[model_name]
        if not current_model:
            return False

        # Traverse the path
        for i, field_name in enumerate(path_parts):
            if field_name not in current_model._fields:
                return False  # Field doesn't exist

            field = current_model._fields[field_name]
            if i < len(path_parts) - 1:  # Not the last part, should be a relation
                if field.type not in ["many2one", "one2many", "many2many"]:
                    return False  # Can't traverse further on non-relation field
                # Move to the related model
                current_model = self.env[field.comodel_name]
                if not current_model:
                    return False

        return True

    def action_validate_field(self):
        """Manual validation action for the field."""
        self.ensure_one()
        is_valid = self._validate_dotted_path()
        if is_valid:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": f'The dotted path "{self.odoo_field_value}" is valid.',
                    "type": "success",
                    "sticky": False,
                },
            }
        else:
            message = self.env._(
                'The dotted path "{path}" is invalid for model "{model}".'
            ).format(
                path=self.odoo_field_value,
                model=self.report_form_id.model_id.name,
            )
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Error",
                    "message": message,
                    "type": "danger",
                    "sticky": True,
                },
            }

    @api.constrains("odoo_field_evaluation", "odoo_field_value", "report_form_id")
    def _check_dotted_path(self):
        for record in self:
            if not record._validate_dotted_path():
                message = self.env._(
                    "The dotted path '{path}' is not valid for model '{model}'."
                ).format(
                    path=record.odoo_field_value,
                    model=record.report_form_id.model_id.name,
                )
                raise ValidationError(message)
