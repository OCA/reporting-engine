# Copyright (C) 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo.addons.web.controllers import main as report
from odoo.http import route, request

import json


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'pdf-combination':
            report = request.env['ir.actions.report']._get_report_from_name(reportname)
            return self._report_pdf_combination(report, docids, converter, **data)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )

    def _report_pdf_combination_sudo(self, reportname, docids=None, converter=None, **data):
        report = request.env['ir.actions.report'].sudo()._get_report_from_name(reportname)
        return self._report_pdf_combination(report, docids, converter, **data)


    def _report_pdf_combination(self, report, docids=None, converter=None, **data):
        context = dict(request.env.context)
        if docids:
            docids = [int(i) for i in docids.split(',')]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the one
            # from the webclient *but* if the user explicitely wants to
            # change the lang, this mechanism overwrites it.
            data['context'] = json.loads(data['context'])
            if data['context'].get('lang'):
                del data['context']['lang']
            context.update(data['context'])
        file_read = report.with_context(context).render_pdf_combination(
            docids, data=data
        )[0]
        httpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(file_read)),
            (
                'Content-Disposition',
                'attachment; filename=' + report.report_file + '.pdf'
            )
        ]
        return request.make_response(file_read, headers=httpheaders)
