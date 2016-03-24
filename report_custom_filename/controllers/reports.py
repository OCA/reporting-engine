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
from openerp.addons.web import http
from openerp.addons.web.controllers import main


class Reports(main.Reports):

    @http.httprequest
    def index(self, req, action, token):
        result = super(Reports, self).index(req, action, token)
        action = simplejson.loads(action)
        context = dict(req.context)
        context.update(action["context"])
        report_xml = req.session.model('ir.actions.report.xml')
        generated_filename = report_xml.generate_filename(
            action['report_name'], context)
        if generated_filename:
            result.headers['Content-Disposition'] = main.content_disposition(
                generated_filename, req)
        return result
