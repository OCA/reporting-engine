# -*- coding: utf-8 -*-
# Copyright (C) 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).
import json
import time

from werkzeug import url_decode

from odoo.addons.report.controllers import main as report
from odoo.http import route, request
from odoo.tools.safe_eval import safe_eval
from odoo.addons.web.controllers.main import (
    _serialize_exception,
    content_disposition
)
from odoo.tools import html_escape


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'csv':
            report = request.env['report']._get_report_from_name(
                reportname)
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

            csv = request.env["report"].with_context(context).get_csv(
                docids, reportname, data=data
            )[0]
            filename = "%s.%s" % (report.name, "csv")
            if docids:
                obj = request.env[report.model].browse(docids)
                if report.print_report_name and not len(obj) > 1:
                    report_name = safe_eval(
                        report.print_report_name,
                        {'object': obj, 'time': time, 'multi': False})
                    filename = "%s.%s" % (report_name, "csv")
                # When we print multiple records we still allow a custom
                # filename.
                elif report.print_report_name and len(obj) > 1:
                    report_name = safe_eval(
                        report.print_report_name,
                        {'objects': obj, 'time': time, 'multi': True})
                    filename = "%s.%s" % (report_name, "csv")
            csvhttpheaders = [
                ('Content-Type', 'text/csv'),
                ('Content-Length', len(csv)),
                (
                    'Content-Disposition',
                    content_disposition(filename)
                )
            ]
            return request.make_response(csv, headers=csvhttpheaders)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )

    @route()
    def report_download(self, data, token):
        """This function is used by 'qwebactionmanager.js' in order to trigger
        the download of a csv/controller report.

        :param data: a javascript array JSON.stringified containg report
        internal url ([0]) and type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        if type != 'csv':
            return super(ReportController, self).report_download(data, token)
        try:
            reportname = url.split('/report/csv/')[1].split('?')[0]
            docids = None
            if '/' in reportname:
                reportname, docids = reportname.split('/')

            if docids:
                # Generic report:
                response = self.report_routes(
                    reportname, docids=docids, converter='csv')
            else:
                # Particular report:
                # decoding the args represented in JSON
                data = url_decode(url.split('?')[1]).items()
                response = self.report_routes(
                    reportname, converter='csv', **dict(data))
            response.set_cookie('fileToken', token)
            return response
        except Exception, e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
