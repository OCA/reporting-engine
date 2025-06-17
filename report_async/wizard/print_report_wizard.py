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

    @api.onchange("reference")
    def _onchange_reference(self):
        self.ensure_one()
        domain = [("id", "in", [])]
        self.action_report_id = False
        if self.reference:
            domain = [("model", "=", self.reference._name)]
        return {"domain": {"action_report_id": domain}}

    def print_report(self):
        self.ensure_one()
        return self.action_report_id.report_action(self.reference, config=False)
