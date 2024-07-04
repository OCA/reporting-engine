# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models

# Define all supported report_type
REPORT_TYPES = ["qweb-pdf", "qweb-text", "qweb-xml", "csv", "excel", "xlsx"]


class Report(models.Model):
    _inherit = "ir.actions.report"

    @api.noguess
    def report_action(self, docids, data=None, config=True):
        res = super(Report, self).report_action(docids, data=data, config=config)
        if res["context"].get("async_process", False):
            rpt_async_id = res["context"]["active_id"]
            report_async = self.env["report.async"].browse(rpt_async_id)
            if res["report_type"] in REPORT_TYPES:
                job = report_async.with_delay(
                    eta=res["context"].get("eta", False)
                ).run_report(
                    res["context"].get("active_ids", []), data, self.id, self._uid
                )
                if job:
                    (self.env['queue.job'].search([('uuid', '=', job.uuid)])
                     .write({'report_async_id': report_async.id}))
                return {}
        return res
