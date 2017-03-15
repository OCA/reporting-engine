# -*- coding: utf-8 -*-
# © 2016 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tools.safe_eval import safe_eval
from openerp.addons.web.http import route, request
from openerp.addons.report.controllers.main import ReportController
from openerp.addons.web.controllers.main import _serialize_exception,\
    content_disposition
from openerp.tools import html_escape

import time
import json
from werkzeug import url_decode
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse
from werkzeug.datastructures import Headers


class ReportController(ReportController):

    @route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        """This function is used by 'qwebactionmanager.js' in order to trigger
        the download of a pdf/controller report.

        :param data: a javascript array JSON.stringified containg report
            internal url ([0]) and
        type [1]
        :returns: Response with a file token cookie and an attachment header
        """
        requestcontent = json.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        try:
            if report_type == 'qweb-pdf':
                reportname = url.split('/report/pdf/')[1].split('?')[0]

                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')

                if docids:
                    # Generic report:
                    response = self.report_routes(reportname, docids=docids,
                                                  converter='pdf')
                else:
                    # Particular report:
                    data = url_decode(url.split('?')[1]).items()
                    # decoding the args represented in JSON
                    response = self.report_routes(reportname, converter='pdf',
                                                  **dict(data))

                report = request.env['report'].\
                    _get_report_from_name(reportname)
                filename = "%s.%s" % (report.name, "pdf")

                # Start of dynamic report name
                # Dynamic name will be taken from attachment option
                if docids and report.attachment:
                    ids = [int(x) for x in docids.split(",")]
                    obj = request.env[report.model].browse(ids)
                    if not len(obj) > 1:
                        filename = safe_eval(report.attachment, {'object': obj,
                                                                 'time': time})
                # End of dynamic report name

                response.headers.add('Content-Disposition',
                                     content_disposition(filename))
                response.set_cookie('fileToken', token)
                return response
            elif report_type == 'controller':
                reqheaders = Headers(request.httprequest.headers)
                response = Client(request.httprequest.app, BaseResponse).get(
                    url, headers=reqheaders, follow_redirects=True
                )
                response.set_cookie('fileToken', token)
                return response
            else:
                return
        except Exception, e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))
