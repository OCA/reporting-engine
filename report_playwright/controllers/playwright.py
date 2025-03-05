import json
import logging

from werkzeug.exceptions import InternalServerError
from werkzeug.urls import url_parse

from odoo.http import content_disposition, request, route, serialize_exception
from odoo.tools.misc import html_escape
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers.report import ReportController

_logger = logging.getLogger(__name__)


class ReportController(ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report = request.env["ir.actions.report"]
        context = dict(request.env.context)

        if converter != "playwright-pdf":
            return super().report_routes(
                reportname=reportname, docids=docids, converter=converter, **data
            )

        if docids:
            docids = [int(i) for i in docids.split(",") if i.isdigit()]
        if data.get("options"):
            data.update(json.loads(data.pop("options")))
        if data.get("context"):
            data["context"] = json.loads(data["context"])
            context.update(data["context"])

        pdf = report.with_context(**context)._render_playwright_pdf(
            reportname, docids, data=data
        )[0]
        pdfhttpheaders = [
            ("Content-Type", "application/pdf"),
            ("Content-Length", len(pdf)),
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @route()
    def report_download(
        self, data, context=None, token=None
    ):  # pylint: disable=unused-argument
        requestcontent = json.loads(data)
        url, type_ = requestcontent[0], requestcontent[1]
        reportname = "???"

        try:
            if type_ == "playwright-pdf":
                converter = "playwright-pdf"

                pattern = "/report/html/"
                reportname = url.split(pattern)[1].split("?")[0]

                docids = None
                if "/" in reportname:
                    reportname, docids = reportname.split("/")

                parsed_url = url_parse(url)
                data = parsed_url.decode_query(cls=dict)
                data["path"] = parsed_url.path

                if docids:
                    # Generic report:
                    response = self.report_routes(
                        reportname, docids=docids, converter=converter, **data
                    )
                else:
                    # Particular report:
                    if "context" in data:
                        context, data_context = json.loads(context or "{}"), json.loads(
                            data.pop("context")
                        )
                        context = json.dumps({**context, **data_context})
                    response = self.report_routes(
                        reportname, converter=converter, context=context, **data
                    )

                report = request.env["ir.actions.report"]._get_report_from_name(
                    reportname
                )
                filename = "%s.%s" % (report.name, "pdf")

                if docids:
                    ids = [int(x) for x in docids.split(",") if x.isdigit()]
                    obj = request.env[report.model].browse(ids)
                    if report.print_report_name and not len(obj) > 1:
                        report_name = safe_eval(
                            report.print_report_name, {"object": obj, "time": time}
                        )
                        filename = "%s.%s" % (report_name, "pdf")

                response.headers.add(
                    "Content-Disposition", content_disposition(filename)
                )

                return response
            else:
                return super().report_download(data, context=context, token=token)
        except Exception as e:
            _logger.exception("Error while generating report %s", reportname)
            se = serialize_exception(e)
            error = {"code": 200, "message": "Odoo Server Error", "data": se}
            res = request.make_response(html_escape(json.dumps(error)))
            raise InternalServerError(response=res) from e
