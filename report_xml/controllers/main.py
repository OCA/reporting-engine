# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import json

from werkzeug.urls import url_decode

from odoo.http import content_disposition, request, route, serialize_exception
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers import main as report


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == "xml":
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

            xml = report.with_context(context)._render_qweb_xml(docids, data=data)[0]
            xmlhttpheaders = [
                ("Content-Type", "text/xml"),
                ("Content-Length", len(xml)),
            ]
            return request.make_response(xml, headers=xmlhttpheaders)
        else:
            return super().report_routes(reportname, docids, converter, **data)

    @route()
    def report_download(self, data, token, context=None):
        requestcontent = json.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        if report_type == "qweb-xml":
            try:
                reportname = url.split("/report/xml/")[1].split("?")[0]

                docids = None
                if "/" in reportname:
                    reportname, docids = reportname.split("/")

                if docids:
                    # Generic report:
                    response = self.report_routes(
                        reportname, docids=docids, converter="xml", context=context
                    )
                else:
                    # Particular report:
                    # decoding the args represented in JSON
                    data = dict(url_decode(url.split("?")[1]).items())
                    if "context" in data:
                        context = json.loads(context or "{}")
                        data_context = json.loads(data.pop("context"))
                        context = json.dumps({**context, **data_context})
                    response = self.report_routes(
                        reportname, converter="xml", context=context, **data
                    )

                report_obj = request.env["ir.actions.report"]
                report = report_obj._get_report_from_name(reportname)
                filename = "%s.xml" % (report.name)

                if docids:
                    ids = [int(doc_id) for doc_id in docids.split(",")]
                    records = request.env[report.model].browse(ids)
                    if report.print_report_name and not len(records) > 1:
                        report_name = safe_eval(
                            report.print_report_name, {"object": records, "time": time}
                        )
                        filename = "{}.xml".format(report_name)
                response.headers.add(
                    "Content-Disposition", content_disposition(filename)
                )
                response.set_cookie("fileToken", token)
                return response
            except Exception as e:
                se = serialize_exception(e)
                error = {"code": 200, "message": "Odoo Server Error", "data": se}
                return request.make_response(html_escape(json.dumps(error)))
        else:
            return super().report_download(data, token, context)
