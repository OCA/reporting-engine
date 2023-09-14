# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import json
import logging

from werkzeug.urls import url_parse

from odoo.http import content_disposition, request, route, serialize_exception
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers import report

_logger = logging.getLogger(__name__)


class ReportController(report.ReportController):
    @route()
    def report_routes(
        self, reportname, docids=None, converter=None, options=None, **kwargs
    ):
        if converter != "xml":
            return super().report_routes(
                reportname,
                docids=docids,
                converter=converter,
                options=options,
                **kwargs,
            )
        if docids:
            docids = [int(_id) for _id in docids.split(",")]
        data = {**json.loads(options or "{}"), **kwargs}
        context = dict(request.env.context)
        if "context" in data:
            data["context"] = json.loads(data["context"] or "{}")
            # Ignore 'lang' here, because the context in data is the one from the
            # webclient *but* if the user explicitely wants to change the lang, this
            # mechanism overwrites it.
            if "lang" in data["context"]:
                del data["context"]["lang"]
            context.update(data["context"])
        report_Obj = request.env["ir.actions.report"]
        xml = report_Obj.with_context(**context)._render_qweb_xml(
            reportname, docids, data=data
        )[0]
        xmlhttpheaders = [("Content-Type", "text/xml"), ("Content-Length", len(xml))]
        return request.make_response(xml, headers=xmlhttpheaders)

    @route()
    def report_download(self, data, context=None, token=None):
        requestcontent = json.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        reportname = "???"
        if report_type != "qweb-xml":
            return super().report_download(data, context=context, token=token)
        try:
            reportname = url.split("/report/xml/")[1].split("?")[0]
            docids = None
            if "/" in reportname:
                reportname, docids = reportname.split("/")
            report = request.env["ir.actions.report"]._get_report_from_name(reportname)
            filename = None
            if docids:
                response = self.report_routes(
                    reportname, docids=docids, converter="xml", context=context
                )
                ids = [int(x) for x in docids.split(",")]
                obj = request.env[report.model].browse(ids)
                if report.print_report_name and not len(obj) > 1:
                    report_name = safe_eval(
                        report.print_report_name, {"object": obj, "time": time}
                    )
                    filename = f"{report_name}.{report.xml_extension}"
            else:
                data = url_parse(url).decode_query(cls=dict)
                if "context" in data:
                    context = json.loads(context or "{}")
                    data_context = json.loads(data.pop("context"))
                    context = json.dumps({**context, **data_context})
                response = self.report_routes(
                    reportname, converter="xml", context=context, **data
                )
            filename = filename or f"{report.name}.{report.xml_extension}"
            response.headers.add("Content-Disposition", content_disposition(filename))
            return response
        except Exception as e:
            _logger.exception(f"Error while generating report {reportname}")
            se = serialize_exception(e)
            error = {"code": 200, "message": "Odoo Server Error", "data": se}
            return request.make_response(html_escape(json.dumps(error)))
