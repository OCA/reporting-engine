# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models

# Define all supported report_type
REPORT_TYPES = ["qweb-pdf", "qweb-text", "qweb-xml", "csv", "excel", "xlsx"]


class Report(models.Model):
    _inherit = "ir.actions.report"

    async_report = fields.Boolean(default=False)
    async_no_records = fields.Integer(
        string="Min of Records",
        default=100,
        help="Min no of records to use async report functionality; e.g 100+",
    )
    async_mail_recipient = fields.Char(
        string="Mail Recipient",
        help="The email that will receive the async report",
        default=lambda self: self.env.user.email,
    )

    def report_action(self, docids, data=None, config=True):
        res = super(Report, self).report_action(docids, data=data, config=config)
        if res["context"].get("async_process", False):
            rpt_async_id = res["context"]["active_id"]
            report_async = self.env["report.async"].browse(rpt_async_id)
            if res["report_type"] in REPORT_TYPES:
                report_async.with_delay().run_report(
                    res["context"].get("active_ids", []), data, self.id, self._uid
                )
                return {}
        return res
