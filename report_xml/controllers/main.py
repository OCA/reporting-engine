# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import time

from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, request, route
from odoo.tools.safe_eval import safe_eval


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        # Trick the main reporter to think we want an HTML report
        new_converter = converter if converter != "xml" else "html"
        response = super(ReportController, self).report_routes(
            reportname, docids, new_converter, **data)

        # If it was an XML report, just download the generated response
        if converter == "xml":
            # XML header must be before any spaces, and it is a common error,
            # so let's fix that here and make developers happier
            response.data = response.data.strip()
            response.headers.set("Content-Type", "text/xml")
            response.headers.set('Content-length', len(response.data))
            # set filename
            action_report_obj = request.env['ir.actions.report']
            report = action_report_obj._get_report_from_name(reportname)
            filename = report.name
            if docids:
                ids = [int(x) for x in docids.split(",")]
                records = request.env[report.model].browse(ids)
                if report.print_report_name and not len(records) > 1:
                    filename = safe_eval(report.print_report_name,
                                         {'object': records, 'time': time})
            response.headers.set(
                'Content-Disposition',
                content_disposition(filename + ".xml"))
        return response
