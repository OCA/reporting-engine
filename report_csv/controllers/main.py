# Copyright (C) 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import json
import logging

from werkzeug.exceptions import InternalServerError
from werkzeug.urls import url_decode

from odoo.http import (
    content_disposition,
    request,
    route,
    serialize_exception as _serialize_exception,
)
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers import report

_logger = logging.getLogger(__name__)


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == "csv":
            report = request.env["ir.actions.report"]._get_report_from_name(reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(",")]
            if data.get("options"):
                data.update(json.loads(data.pop("options")))
            if data.get("context"):
                # Ignore 'lang' here, because the context in data is the one
                # from the webclient *but* if the user explicitely wants to
                # change the lang, this mechanism overwrites it.
                data["context"] = json.loads(data["context"])
                if data["context"].get("lang"):
                    del data["context"]["lang"]
                context.update(data["context"])
            csv = report.with_context(**context)._render_csv(
                reportname, docids, data=data
            )[0]
            csvhttpheaders = [
                ("Content-Type", "text/csv"),
                ("Content-Length", len(csv)),
            ]
            return request.make_response(csv, headers=csvhttpheaders)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )

    @route()
    def report_download(self, data, context=None):
        requestcontent = json.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        reportname = ""
        try:
            if report_type == "csv":
                reportname = url.split("/report/csv/")[1].split("?")[0]
                docids = None
                if "/" in reportname:
                    reportname, docids = reportname.split("/")
                if docids:
                    # Generic report:
                    response = self.report_routes(
                        reportname, docids=docids, converter="csv", context=context
                    )
                else:
                    # Particular report:
                    data = dict(
                        url_decode(url.split("?")[1]).items()
                    )  # decoding the args represented in JSON
                    if "context" in data:
                        context, data_context = json.loads(context or "{}"), json.loads(
                            data.pop("context")
                        )
                        context = json.dumps({**context, **data_context})
                    response = self.report_routes(
                        reportname, converter="csv", context=context, **data
                    )

                report = request.env["ir.actions.report"]._get_report_from_name(
                    reportname
                )
                filename = "%s.%s" % (report.name, "csv")

                if docids:
                    ids = [int(x) for x in docids.split(",")]
                    obj = request.env[report.model].browse(ids)
                    if report.print_report_name and not len(obj) > 1:
                        report_name = safe_eval(
                            report.print_report_name, {"object": obj, "time": time}
                        )
                        filename = "%s.%s" % (report_name, "csv")
                response.headers.add(
                    "Content-Disposition", content_disposition(filename)
                )
                return response
            else:
                return super(ReportController, self).report_download(data, context)
        except Exception as e:
            _logger.exception("Error while generating report %s", reportname)
            se = _serialize_exception(e)
            error = {"code": 200, "message": "Odoo Server Error", "data": se}
            res = request.make_response(html_escape(json.dumps(error)))
            raise InternalServerError(response=res) from e
