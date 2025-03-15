# Copyright 2025 Hunki Enterprises BV <https://hunki-enterprises.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import time

from markupsafe import Markup
from weasyprint import HTML, default_url_fetcher
from werkzeug.test import EnvironBuilder

from odoo import fields, http, models

BASE_URL = "odoo://"


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    qweb_pdf_engine = fields.Selection(
        selection_add=[("weasyprint", "WeasyPrint")],
    )
    weasyprint_header_height = fields.Float(
        "Header height",
        help="Header height in mm",
    )
    weasyprint_footer_height = fields.Float(
        "Footer height",
        help="Footer height in mm",
    )

    def _render_qweb_pdf_weasyprint(self, report_ref, res_ids=None, data=None):
        render_context = self._weasyprint_get_render_context(
            report_ref, res_ids, data=data
        )

        html = self._render_qweb_html(
            report_ref,
            res_ids,
            data=render_context,
        )[0]
        self._weasyprint_set_loglevels()

        if not html.lstrip().startswith(b"<html>"):
            html = self.env["ir.ui.view"]._render_template(
                "report_qweb_weasyprint_renderer.html_wrapper_wkhtml_compat",
                dict(render_context, body=Markup(html.decode("utf8"))),
            )
        return (
            HTML(
                string=html,
                url_fetcher=lambda url, *args, **kwargs: self._weasyprint_url_fetcher(
                    url, render_context, *args, **kwargs
                ),
                base_url=BASE_URL,
                # base_url=self.env['ir.config_parameter'].get_param('report.url'),
            ).write_pdf(
                pdf_forms=True,
            ),
            "pdf",
        )

    def _weasyprint_url_fetcher(self, url, render_context, *args, **kwargs):
        if not url.startswith("odoo:") and not url.startswith("/"):
            return default_url_fetcher(url, *args, **kwargs)

        if url.startswith(BASE_URL):
            url = url[len(BASE_URL) :]
            if not url:
                return {
                    "string": b"",
                }

        parts = list(filter(lambda x: x and x not in (".", ".."), url.split("/")))
        if len(parts) > 2 and parts[1] == "static":
            file = "/".join([http.root.statics[parts[0]]] + parts[2:])
            return default_url_fetcher(f"file://{file}", *args, **kwargs)

        with http.HTTPRequest(EnvironBuilder().get_environ()) as httprequest:
            request = http.Request(httprequest)
            request.env = self.env
            request.db = self.env.cr.dbname
            http._request_stack.push(request)
            try:
                handler, args = (
                    self.env["ir.http"]
                    .routing_map()
                    .bind_to_environ(request.httprequest.environ)
                    .match(url)
                )
                result = handler(**args)
                result.flatten()
                data = result.response.file.read()
            finally:
                http._request_stack.pop()

        return {
            "string": data,
            "mime_type": result.mimetype,
        }

    def _weasyprint_set_loglevels(self):
        logging.getLogger("weasyprint").setLevel(logging.ERROR)
        logging.getLogger("fontTools.subset").setLevel(logging.ERROR)
        logging.getLogger("fontTools.ttLib.ttFont").setLevel(logging.ERROR)
        logging.getLogger("fontTools.ttLib.woff2").setLevel(logging.ERROR)

    def _weasyprint_get_render_context(self, report_ref, res_ids=None, data=None):
        return dict(
            company=self.env.company,
            report=self._get_report(report_ref),
            report_type="pdf",
            time=time,
            user=self.env.user,
            o=self.env.user,
            **(data or {}),
        )
