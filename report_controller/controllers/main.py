# Copyright 2018 Hugo Rodrigues
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from werkzeug.urls import url_decode


from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval
from odoo.http import request, route, serialize_exception, content_disposition
from odoo.addons.web.controllers.main import ReportController
from ..models.ir_actions_report import CONTROLLER_KEYS

class Report(ReportController):


    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        """
        Extends de base controller to download controller reports
        """
        if converter not in CONTROLLER_KEYS:
            return super(Report, self).report_routes(reportname, docids=docids,
                                                     converter=converter,
                                                     **data)
        report = request.env['ir.actions.report']._get_report_from_name(reportname)
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(',')]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the one from the webclient *but* if
            # the user explicitely wants to change the lang, this mechanism overwrites it.
            data['context'] = json.loads(data['context'])
            if data['context'].get('lang'):
                del data['context']['lang']
            context.update(data['context'])

        if converter == 'controller':
            pdf = report.with_context(context).render_controller(docids,
                                                                 data=data)[0]
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else:
            raise werkzeug.exceptions.HTTPException(description='Converter %s not implemented.' % converter)

    @route()
    def report_download(self, data, token):
        """
        Extends de base controller to download controller reports
        
        :param data: a javascript array JSON.stringified containg
                     report internal url ([0]) and type [1]
        :returns: Response with a filetoken cookie and an attachment heade
        """
        rcontent = json.loads(data)
        url, rtype = rcontent[0], rcontent[1]
        # Return error as upstream
        try:
            if rtype not in CONTROLLER_KEYS:
                return super(Report, self).report_download(data, token)
            if rtype == "controller":
                # Based on upstream
                # addons/web/controllers/main.py:1649
                reportname = url.split("/report/controller/")[1].split("?")[0]
                docids = None
                if "/" in reportname:
                    reportname, docids = reportname.split("/")

                if docids:
                    response = self.report_routes(reportname, docids=docids,
                                                  converter="controller")
                else:
                    data = url_decode(url.split("?")[1]).items()
                    reponse = self.report_routes(reportname,
                                                 converter=converter,
                                                 **dict(data))
                report = request.env["ir.actions.report"]._get_report_from_name(reportname)
                filename = "%s.pdf" % (report.name)

                if docids:
                    ids = [int(x) for x in docids.split(",")]
                    obj = request.env[report.model].browse(ids)
                    if report.print_report_name and not len(obj) > 1:
                        report_name = safe_eval(report.print_report_name,
                                                {"object": obj, "time": time})
                        filename = "%s.%s" % (report_name, extension)
                response.headers.add("Content-Disposition",
                                     content_disposition(filename))
                response.set_cookie("fileToken", token)
                return response
            return
        except Exception as e:
            se = serialize_exception(e)
            error = {
                "code": 200,
                "message": "Odoo Server Error",
                "data": se
                }
            return request.make_response(html_escape(json.dumps(error)))
