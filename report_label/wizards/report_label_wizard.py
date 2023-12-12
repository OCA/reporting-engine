# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ReportLabelWizard(models.TransientModel):
    _name = "report.label.wizard"
    _description = "Report Label Wizard"

    @api.model
    def _default_line_ids(self):
        """Compute line_ids based on context"""
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids", [])
        if not active_model or not active_ids:
            return False
        return [
            (
                0,
                0,
                {
                    "res_id": res_id,
                    "quantity": 1,
                },
            )
            for res_id in active_ids
        ]

    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        default=lambda self: self.env.context.get("res_model_id"),
    )
    label_paperformat_id = fields.Many2one(
        "report.paperformat.label",
        "Label Paper Format",
        readonly=True,
        required=True,
        default=lambda self: self.env.context.get("label_paperformat_id"),
    )

    label_template_view_id = fields.Many2one(
        string="Label QWeb Template",
        comodel_name="ir.ui.view",
        readonly=True,
        required=True,
        default=lambda self: self.env.context.get("label_template_view_id"),
    )
    offset = fields.Integer(
        help="Number of labels to skip when printing",
    )
    line_ids = fields.One2many(
        "report.label.wizard.line",
        "wizard_id",
        "Lines",
        default=_default_line_ids,
        required=True,
    )

    def _prepare_report_data(self):
        self.ensure_one()
        return {
            "label_format": self.label_paperformat_id.read()[0],
            "label_template": self.label_template_view_id.sudo().key,
            "offset": self.offset,
            "res_model": self.model_id.sudo().model,
            "lines": [
                {
                    "res_id": line.res_id,
                    "quantity": line.quantity,
                }
                for line in self.line_ids
            ],
        }

    def print_report(self):
        self.ensure_one()
        report = self.env.ref("report_label.report_label")
        action = report.report_action(self, data=self._prepare_report_data())
        action["context"] = {
            "paperformat_id": self.label_paperformat_id.paperformat_id.id,
        }
        return action
