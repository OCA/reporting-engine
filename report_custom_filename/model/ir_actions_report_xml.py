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
from openerp.osv import fields, orm
from openerp.addons.email_template.email_template import mako_template_env


class IrActionsReportXml(orm.Model):
    _inherit = 'ir.actions.report.xml'

    _columns = {
        'download_filename': fields.char(
            'Download filename',
            help='Fill in this field to have a custom file name when '
            'downloading this report. This string is evaluated as a jinja2 '
            'expression.\nYou can use python expressions, `objects` is a '
            'browse record list of the objects for which the report is being '
            'generated.\nCheck for this list\'s length to determine if it is '
            'a report being printed for multiple records or not. You also '
            'have access to `o`, which is the first record in the list')
        }

    def generate_filename(self, cr, uid, report_name, context=None):
        report_ids = self.search(
            cr, uid, [('report_name', '=', report_name),
                      ('download_filename', '!=', False)],
            limit=1, context=context)
        for report in self.browse(cr, uid, report_ids, context=context):
            objects = self.pool[context['active_model']].browse(
                cr, uid, context['active_ids'], context=context)
            return mako_template_env.from_string(
                report.download_filename).render({
                    'objects': objects,
                    'o': objects[0],
                    'object': objects[0],
                })
        return False
