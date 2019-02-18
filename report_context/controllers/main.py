# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.web.controllers import main as report
from odoo.http import route, request
import json


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report = request.env['ir.actions.report']._get_report_from_name(
            reportname)
        original_context = json.loads(data.get('context', '{}'))
        data['context'] = json.dumps(report.with_context(
            original_context
        )._get_context())
        return super().report_routes(
            reportname, docids=docids, converter=converter, **data)
