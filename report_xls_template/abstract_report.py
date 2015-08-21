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

from openerp.osv import osv


class AbstractReport(osv.AbstractModel):
    """Model used to embed old style reports"""

    _inherit = 'report.abstract_report'
    _report_render_type = None

    def render_html(self, cr, uid, ids, data=None, context=None):

        if self._report_render_type == 'qweb-xls':
            context = dict(context or {})

            if context and context.get('active_ids'):
                # Browse the selected objects via their reference in context
                model = context.get('active_model') or context.get('model')
                objects_model = self.pool[model]
                objects = objects_model.browse(
                    cr, uid, context['active_ids'], context=context)
            else:
                # If no context is set (for instance,
                # during test execution), build one
                model = self.pool['report']._get_xls_report_from_name(
                    cr, uid, self._template).model
                objects_model = self.pool[model]
                objects = objects_model.browse(cr, uid, ids, context=context)
                context['active_model'] = model
                context['active_ids'] = ids

            # Generate the old style report
            wrapped_report = self._wrapped_report_class(
                cr, uid, '',  context=context)
            wrapped_report.set_context(
                objects, data, context['active_ids'])

            # Rendering self._template with the wrapped
            # report instance localcontext as
            # rendering environment
            docargs = dict(wrapped_report.localcontext)
            if not docargs.get('lang'):
                docargs.pop('lang', False)
            docargs['docs'] = docargs.get('objects')

            # Used in template translation (see
            # translate_doc method from report model)
            docargs['doc_ids'] = context['active_ids']
            docargs['doc_model'] = model

            return self.pool['report'].render(
                cr, uid, [], self._template, docargs, context=context)
        else:
            return super(AbstractReport, self).render_html(
                cr, uid, ids, data=data, context=context)
