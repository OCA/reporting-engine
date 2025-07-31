# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class PrintReportWizard(models.TransientModel):
    _name = "print.report.wizard"
    _description = "Print Report Wizard"

    reference = fields.Reference(
        string="Document",
        selection="_reference_models",
        required=True,
    )
    reference_model = fields.Char(compute="_compute_reference_model")
    action_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Report Template",
        required=True,
    )

    @api.model
    def _reference_models(self):
        excludes = ["res.company"]
        models = self.env["ir.model"].search(
            [
                ("state", "!=", "manual"),
                ("transient", "=", False),
                ("model", "not in", excludes),
            ]
        )
        return [(model.model, model.name) for model in models]

    @api.depends("reference")
    def _compute_reference_model(self):
        for record in self:
            if record.reference:
                record.reference_model = record.reference._name
            else:
                record.reference_model = False

    @api.onchange("reference")
    def _onchange_reference(self):
        self.ensure_one()
        self.action_report_id = False

    def print_report(self):
        self.ensure_one()
        return self.action_report_id.report_action(self.reference, config=False)
