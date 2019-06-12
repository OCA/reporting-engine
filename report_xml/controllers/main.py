# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import json
import time

from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, request, route, serialize_exception
from odoo.tools import safe_eval, html_escape
from werkzeug.urls import url_decode


class ReportController(report.ReportController):
    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'xml':
            report = request.env['ir.actions.report']._get_report_from_name(
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

            xml = report.with_context(context).render_qweb_xml(docids,
                                                               data=data)[0]
            xmlhttpheaders = [('Content-Type', 'text/xml'),
                              ('Content-Length', len(xml))]
            return request.make_response(xml, headers=xmlhttpheaders)
        else:
            return super(ReportController, self).report_routes(
                reportname, docids, converter, **data)

    @route()
    def report_download(self, data, token):
        requestcontent = json.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        if report_type == 'qweb-xml':
            try:
                reportname = url.split('/report/xml/')[1].split('?')[0]

                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')

                if docids:
                    # Generic report:
                    response = self.report_routes(
                        reportname, docids=docids, converter='xml')
                else:
                    # Particular report:
                    # decoding the args represented in JSON
                    data = url_decode(url.split('?')[1]).items()
                    response = self.report_routes(
                        reportname, converter='xml', **dict(data))

                report_obj = request.env['ir.actions.report']
                report = report_obj._get_report_from_name(reportname)
                filename = "%s.xml" % (report.name)

                if docids:
                    ids = [int(x) for x in docids.split(",")]
                    records = request.env[report.model].browse(ids)
                    if report.print_report_name and not len(records) > 1:
                        report_name = safe_eval(report.print_report_name,
                                                {'object': records,
                                                 'time': time})
                        filename = "%s.xml" % (report_name)
                response.headers.add('Content-Disposition',
                                     content_disposition(filename))
                response.set_cookie('fileToken', token)
                return response
            except Exception as e:
                se = serialize_exception(e)
                error = {
                    'code': 200,
                    'message': "Odoo Server Error",
                    'data': se
                }
                return request.make_response(html_escape(json.dumps(error)))
        else:
            return super(ReportController, self).report_download(data, token)
