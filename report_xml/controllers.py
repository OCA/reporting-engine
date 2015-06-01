# -*- encoding: utf-8 -*-

# Odoo, Open Source Management Solution
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp.http import route
from openerp.addons.report.controllers import main as report


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

            # XML files should be downloaded
            response.headers.set("Content-Type", "text/xml")

        return response
