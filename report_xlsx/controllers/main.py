# Copyright (C) 2017 Creu Blanca
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import time

from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, route, request
from odoo.tools.safe_eval import safe_eval

import json


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'xlsx':
            report = request.env['ir.actions.report']._get_report_from_name(
                reportname)
            context = dict(request.env.context)
            filename = "%s.%s" % (report.name, "xlsx")
            if docids:
                docids = [int(i) for i in docids.split(',')]
                obj = request.env[report.model].browse(docids)
                if report.print_report_name and not len(obj) > 1:
                    report_name = safe_eval(report.print_report_name,
                                            {'object': obj, 'time': time})
                    filename = "%s.%s" % (report_name, "xlsx")
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
            xlsx = report.with_context(context).render_xlsx(
                docids, data=data
            )[0]
            xlsxhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(xlsx)),
                (
                    'Content-Disposition',
                    content_disposition(filename)
                )
            ]
            return request.make_response(xlsx, headers=xlsxhttpheaders)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )
