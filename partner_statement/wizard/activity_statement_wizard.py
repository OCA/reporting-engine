# Copyright 2018 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ActivityStatementWizard(models.TransientModel):
    """Activity Statement wizard."""

    _inherit = "statement.common.wizard"
    _name = "activity.statement.wizard"
    _description = "Activity Statement Wizard"

    @api.model
    def _get_date_start(self):
        return (
            fields.Date.context_today(self).replace(day=1) - relativedelta(days=1)
        ).replace(day=1)

    date_start = fields.Date(required=True, default=_get_date_start)

    @api.onchange("aging_type")
    def onchange_aging_type(self):
        res = super().onchange_aging_type()
        if self.aging_type == "months":
            self.date_start = self.date_end.replace(day=1)
        else:
            self.date_start = self.date_end - relativedelta(days=30)
        return res

    def _prepare_statement(self):
        res = super()._prepare_statement()
        res.update(
            {
                "date_start": self.date_start,
                "is_activity": True,
            }
        )
        return res

    def _print_report(self, report_type):
        self.ensure_one()
        data = self._prepare_statement()
        if report_type == "xlsx":
            report_name = "p_s.report_activity_statement_xlsx"
        else:
            report_name = "partner_statement.activity_statement"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(self, data=data)
        )

    def _export(self, report_type):
        """Default export is PDF."""
        return self._print_report(report_type)
