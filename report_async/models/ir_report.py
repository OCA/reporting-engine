# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


# Define all supported report_type
REPORT_TYPES = ["qweb-pdf", "qweb-html"]


class Report(models.Model):
    _inherit = "report"

    @api.noguess
    def get_action(self, docids, report_name, data=None):
        res = super(Report, self).get_action(docids, report_name, data=data)
        if res["context"].get("async_process", False):
            rpt_async_id = res["context"]["active_id"]
            report_async = self.env["report.async"].browse(rpt_async_id)
            if res["report_type"] in REPORT_TYPES:
                report_async.with_delay().run_report(
                    res["context"].get("active_ids", []), data, self.id, self._uid
                )
                return {}
        return res
