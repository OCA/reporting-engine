# Copyright 2018 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class DetailedActivityStatementWizard(models.TransientModel):
    """Detailed Activity Statement wizard."""

    _inherit = "activity.statement.wizard"
    _name = "detailed.activity.statement.wizard"
    _description = "Detailed Activity Statement Wizard"

    show_aging_buckets = fields.Boolean(default=False)
    show_balance = fields.Boolean(string="Show Balance column")

    def _prepare_statement(self):
        res = super()._prepare_statement()
        res.update(
            {
                "is_detailed": True,
            }
        )
        return res

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_statement()
        if report_type == "xlsx":
            report_name = "p_s.report_detailed_activity_statement_xlsx"
        else:
            report_name = "partner_statement.detailed_activity_statement"
        partners = self.env["res.partner"].browse(data["partner_ids"])
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(partners, data=data)
        )
