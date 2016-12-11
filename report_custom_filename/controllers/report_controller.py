# -*- coding: utf-8 -*-
# Copyright 2014 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import http
from openerp.addons.mail.models import mail_template
from openerp.addons.report.controllers.main import ReportController
from openerp.addons.web.controllers.main import content_disposition


class ReportController(ReportController):
    @http.route([
        '/report/<path:converter>/<reportname>',
        '/report/<path:converter>/<reportname>/<docids>',
    ])
    def report_routes(self, reportname, docids=None, converter=None, **data):
        response = super(ReportController, self).report_routes(
            reportname, docids=docids, converter=converter, **data)
        if docids:
            docids = [int(i) for i in docids.split(',')]
        report_xml = http.request.session.model('ir.actions.report.xml')
        report_ids = report_xml.search(
            [('report_name', '=', reportname)])
        for report in report_xml.browse(report_ids):
            if not report.download_filename:
                continue
            objects = http.request.session.model(report.model)\
                .browse(docids or [])
            generated_filename = mail_template.mako_template_env\
                .from_string(report.download_filename)\
                .render({
                    'objects': objects,
                    'o': objects[:1],
                    'object': objects[:1],
                    'ext': report.report_type.replace('qweb-', ''),
                })
            response.headers['Content-Disposition'] = content_disposition(
                generated_filename)
        return response

    @http.route(['/report/download'])
    def report_download(self, data, token):
        response = super(ReportController, self).report_download(data, token)
        # if we got another content disposition before, ditch the one added
        # by super()
        last_index = None
        for i in range(len(response.headers) - 1, -1, -1):
            if response.headers[i][0] == 'Content-Disposition':
                if last_index:
                    response.headers.pop(last_index)
                last_index = i
        return response
