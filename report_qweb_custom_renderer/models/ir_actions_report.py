# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import time

from odoo import fields, models

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    qweb_pdf_engine = fields.Selection(
        [("wkhtmltopdf", "wkhtmltopdf")],
        default="wkhtmltopdf",
        string="PDF Engine",
    )

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        qweb_pdf_engine = "wkhtmltopdf"
        qweb_pdf_engine = "weasyprint"

        _logger.info("========================================")
        _logger.info("=================<begin> render_qweb_pdf")
        _logger.info("========================================")
        time_1 = time.time()
        if qweb_pdf_engine == "wkhtmltopdf":
            result = super()._render_qweb_pdf(
                report_ref,
                res_ids=res_ids,
                data=data,
            )
        else:
            result = getattr(self, "_render_qweb_pdf_%s" % qweb_pdf_engine)(
                report_ref,
                res_ids=res_ids,
                data=data,
            )
        time_2 = time.time()
        _logger.info("%s: %s seconds" % (qweb_pdf_engine, time_2 - time_1))
        _logger.info("========================================")
        _logger.info("=================<end> render_qweb_pdf")
        _logger.info("========================================")
        return result
