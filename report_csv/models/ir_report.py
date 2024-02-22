# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("csv", "csv")], ondelete={"csv": "set default"}
    )

    @api.model
    def _render_csv(self, report_ref, docids, data):
        report_sudo = self._get_report(report_ref)
        report_model_name = "report.%s" % report_sudo.report_name
        report_model = self.env[report_model_name]
        return report_model.with_context(
            active_model=report_sudo.model
        ).create_csv_report(docids, data)

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env["ir.actions.report"]
        qwebtypes = ["csv"]
        conditions = [
            ("report_type", "in", qwebtypes),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        return report_obj.with_context(**context).search(conditions, limit=1)
