# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, route


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
            response.headers.set(
                'Content-Disposition',
                content_disposition(reportname + ".xml"))
        return response
