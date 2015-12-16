# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
import simplejson
from openerp import http
from openerp.addons.web.controllers import main
from openerp.addons.email_template import email_template


class Reports(main.Reports):
    @http.route('/web/report', type='http', auth="user")
    @main.serialize_exception
    def index(self, action, token):
        result = super(Reports, self).index(action, token)
        action = simplejson.loads(action)
        context = dict(http.request.context)
        context.update(action["context"])
        report_xml = http.request.session.model('ir.actions.report.xml')
        report_ids = report_xml.search(
            [('report_name', '=', action['report_name'])],
            0, False, False, context=context)
        for report in report_xml.browse(report_ids):
            if not report.download_filename:
                continue
            objects = http.request.session.model(context['active_model'])\
                .browse(context['active_ids'])
            generated_filename = email_template.mako_template_env\
                .from_string(report.download_filename)\
                .render({
                    'objects': objects,
                    'o': objects[0],
                    'object': objects[0],
                })
            result.headers['Content-Disposition'] = main.content_disposition(
                generated_filename)
        return result
