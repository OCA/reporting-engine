# Copyright (C) 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import json
import time

from odoo.http import content_disposition, request, route
from odoo.tools.safe_eval import safe_eval

from odoo.addons.web.controllers import main as report


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
            csv = report.with_context(context).render_csv(docids, data=data)[0]
            filename = "{}.{}".format(report.name, "csv")
            if docids:
                obj = request.env[report.model].browse(docids)
                if report.print_report_name and not len(obj) > 1:
                    report_name = safe_eval(
                        report.print_report_name,
                        {"object": obj, "time": time, "multi": False},
                    )
                    filename = "{}.{}".format(report_name, "csv")
                # When we print multiple records we still allow a custom
                # filename.
                elif report.print_report_name and len(obj) > 1:
                    report_name = safe_eval(
                        report.print_report_name,
                        {"objects": obj, "time": time, "multi": True},
                    )
                    filename = "{}.{}".format(report_name, "csv")
            csvhttpheaders = [
                ("Content-Type", "text/csv"),
                ("Content-Length", len(csv)),
                ("Content-Disposition", content_disposition(filename)),
            ]
            return request.make_response(csv, headers=csvhttpheaders)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )
