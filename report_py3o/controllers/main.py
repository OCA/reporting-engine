# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json
import mimetypes
from werkzeug import exceptions, url_decode

from odoo.http import route, request

from odoo.addons.report.controllers import main
from odoo.addons.web.controllers.main import (
    _serialize_exception,
    content_disposition
)
from odoo.tools import html_escape


class ReportController(main.ReportController):

    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter != 'py3o':
            return super(ReportController, self).report_routes(
                reportname=reportname, docids=docids, converter=converter,
                **data)
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(',')]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the
            # one from the webclient *but* if the user explicitely wants to
            # change the lang, this mechanism overwrites it.
            data['context'] = json.loads(data['context'])
            if data['context'].get('lang'):
                del data['context']['lang']
            context.update(data['context'])

        ir_action = request.env['ir.actions.report.xml']
        action_py3o_report = ir_action.get_from_report_name(
            reportname, "py3o").with_context(context)
        if not action_py3o_report:
            raise exceptions.HTTPException(
                description='Py3o action report not found for report_name '
                            '%s' % reportname)
        context['report_name'] = reportname
        py3o_report = request.env['py3o.report'].create({
            'ir_actions_report_xml_id': action_py3o_report.id
        }).with_context(context)
        res, filetype = py3o_report.create_report(docids, data)
        filename = action_py3o_report.gen_report_download_filename(
            docids, data)
        content_type = mimetypes.guess_type("x." + filetype)[0]
        http_headers = [('Content-Type', content_type),
                        ('Content-Length', len(res)),
                        ('Content-Disposition', content_disposition(filename))
                        ]
        return request.make_response(res, headers=http_headers)

    @route()
    def report_download(self, data, token):
        """This function is used by 'qwebactionmanager.js' in order to trigger
        the download of a py3o/controller report.

        :param data: a javascript array JSON.stringified containg report
        internal url ([0]) and type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        if type != 'py3o':
            return super(ReportController, self).report_download(data, token)
        try:
            reportname = url.split('/report/py3o/')[1].split('?')[0]
            docids = None
            if '/' in reportname:
                reportname, docids = reportname.split('/')

            if docids:
                # Generic report:
                response = self.report_routes(
                    reportname, docids=docids, converter='py3o')
            else:
                # Particular report:
                # decoding the args represented in JSON
                data = url_decode(url.split('?')[1]).items()
                response = self.report_routes(
                    reportname, converter='py3o', **dict(data))
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
