# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from pathlib import Path

from odoo import fields, models

try:
    from weasyprint import HTML, default_url_fetcher
except ImportError:
    HTML = None
    default_url_fetcher = None


_logger = logging.getLogger(__name__)
_weasyprint_logger = logging.getLogger("weasyprint")
_weasyprint_logger.setLevel(logging.DEBUG)


def _weasyprint_url_fetcher(url):
    if False and "/web/static/" in url:
        base, end = url.split("/web/static/")
        file_cool, file_naze = end.split("?")
        file_cool, file_naze = file_cool.split("#")
        file = (
            Path(
                "/home/sylvain/grap_dev/grap-odoo-env-16.0/src/odoo/addons/web/static/"
            )
            / file_cool
        )
        return {"string": file.read_bytes()}
    if "odoocdn" in url:
        return
    return default_url_fetcher(url)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    qweb_pdf_engine = fields.Selection(
        selection_add=[("weasyprint", "WeasyPrint")],
    )

    def _render_qweb_pdf_weasyprint(self, report_ref, res_ids=None, data=None):
        data = data or {}
        data["enable_editor"] = (False,)
        context = dict(self.env.context)
        context["qweb_pdf_engine"] = "weasyprint"

        html = self.with_context(**context)._render_qweb_html(
            report_ref, res_ids, data=data
        )
        with open("/tmp/tralala_weasyprint.html", "wb+") as f:
            f.write(html[0])

        return (
            HTML(
                string=html[0],
                # TODO: pass a custom url fetcher to never actually use the port
                base_url=self.env["ir.config_parameter"].get_param("report.url")
                or self.env["ir.config_parameter"].get_param("web.base.url"),
                url_fetcher=_weasyprint_url_fetcher,
            ).write_pdf(),
            "pdf",
        )
