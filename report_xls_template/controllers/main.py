# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#    Code inspired by OpenERP SA report module
##############################################################################

import simplejson
from werkzeug import exceptions, url_decode
from openerp.osv import osv
from openerp.addons.web.http import Controller, route, request
from openerp.addons.web.controllers.main import _serialize_exception


class ReportXLSController(Controller):

    @route([
        '/reportxlstemplate/<path:converter>/<reportname>',
        '/reportxlstemplate/<path:converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report_obj = request.registry['report']
        cr, uid, context = request.cr, request.uid, request.context

        if docids:
            docids = [int(i) for i in docids.split(',')]
        options_data = None
        if data.get('options'):
            options_data = simplejson.loads(data['options'])
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the
            # one from the webclient *but* if the user explicitely
            # wants to change the lang, this mechanism overwrites it.
            data_context = simplejson.loads(data['context'])
            if data_context.get('lang'):
                del data_context['lang']
            context.update(data_context)

        if converter == 'xls':
            xls = report_obj.get_xls(cr, uid, docids, reportname,
                                     data=options_data, context=context)
            xlshttpheaders = [('Content-Type', 'application/vnd.ms-excel'),
                              ('Content-Length', len(xls))]
            return request.make_response(xls, headers=xlshttpheaders)
        elif converter == 'ods':
            ods = report_obj.get_ods(cr, uid, docids, reportname,
                                     data=options_data, context=context)
            odshttpheaders = [
                ('Content-Type',
                 'application/vnd.oasis.opendocument.spreadsheet'),
                ('Content-Length', len(ods))]
            return request.make_response(ods, headers=odshttpheaders)
        else:
            raise exceptions.HTTPException(
                description='Converter %s not implemented.' % converter)

    @route(['/reportxlstemplate/download'], type='http', auth="user")
    def report_download(self, data, token):
        """This function is used by 'report_xls.js' in order to
        trigger the download of xls/ods report.
        :param data: a javascript array JSON.stringified containg
        report internal url ([0]) and type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        requestcontent = simplejson.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        try:
            if report_type == 'qweb-xls':
                reportname = url.split(
                    '/reportxlstemplate/xls/')[1].split('?')[0]
                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')
                if docids:
                    # Generic report:
                    response = self.report_routes(
                        reportname, docids=docids, converter='xls')
                else:
                    # Particular report:
                    # Decoding the args represented in JSON
                    data = url_decode(url.split('?')[1]).items()
                    response = self.report_routes(
                        reportname, converter='xls', **dict(data))

                response.headers.add(
                    'Content-Disposition',
                    'attachment; filename=%s.xls;' % reportname)
                response.set_cookie('fileToken', token)
                return response
            elif report_type == 'qweb-ods':
                reportname = url.split(
                    '/reportxlstemplate/ods/')[1].split('?')[0]
                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')
                if docids:
                    # Generic report:
                    response = self.report_routes(
                        reportname, docids=docids, converter='ods')
                else:
                    # Particular report:
                    # Decoding the args represented in JSON
                    data = url_decode(url.split('?')[1]).items()
                    response = self.report_routes(
                        reportname, converter='ods', **dict(data))

                response.headers.add(
                    'Content-Disposition',
                    'attachment; filename=%s.ods;' % reportname)
                response.set_cookie('fileToken', token)
                return response
            else:
                return
        except osv.except_osv, e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(simplejson.dumps(error))
