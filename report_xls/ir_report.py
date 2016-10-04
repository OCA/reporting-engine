# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm


class ir_actions_report_xml(orm.Model):
    _inherit = 'ir.actions.report.xml'

    def _check_selection_field_value(self, cr, uid,
                                     field, value, context=None):
        if field == 'report_type' and value == 'xls':
            return
        return super(ir_actions_report_xml, self)._check_selection_field_value(
            cr, uid, field, value, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
