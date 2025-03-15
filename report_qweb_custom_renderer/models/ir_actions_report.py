# Copyright 2025 Hunki Enterprises BV <https://hunki-enterprises.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    qweb_pdf_engine = fields.Selection(
        [("wkhtmltopdf", "wkhtmltopdf")],
        default="wkhtmltopdf",
        string="PDF Engine",
    )

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report = self._get_report(report_ref)
        if report.qweb_pdf_engine == "wkhtmltopdf":
            return super()._render_qweb_pdf(
                report_ref,
                res_ids=res_ids,
                data=data,
            )
        return getattr(self, "_render_qweb_pdf_%s" % report.qweb_pdf_engine)(
            report_ref,
            res_ids=res_ids,
            data=data,
        )
