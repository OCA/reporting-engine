# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class ReportLabelWizardLine(models.TransientModel):
    _name = "report.label.wizard.line"
    _description = "Report Label Wizard Line"
    _order = "sequence"

    wizard_id = fields.Many2one(
        "report.label.wizard",
        "Wizard",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(default=10)
    res_id = fields.Integer("Resource ID", required=True)
    res_name = fields.Char(compute="_compute_res_name")
    quantity = fields.Integer(default=1, required=True)

    @api.depends("wizard_id.model_id", "res_id")
    def _compute_res_name(self):
        wizard = self.mapped("wizard_id")
        wizard.ensure_one()
        res_model = wizard.model_id.sudo().model
        res_ids = self.mapped("res_id")
        names_map = dict(self.env[res_model].browse(res_ids).name_get())
        for rec in self:
            rec.res_name = names_map.get(rec.res_id)
