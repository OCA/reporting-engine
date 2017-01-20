# -*- encoding: utf-8 -*-
# Copyright 2014 Noviat nv/sa (<http://www.noviat.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm


class ir_actions_report_xml(orm.Model):
    _inherit = 'ir.actions.report.xml'

    def _check_selection_field_value(self, cr, uid,
                                     field, value, context=None):
        if field == 'report_type' and value == 'xls':
            return
        return super(ir_actions_report_xml, self)._check_selection_field_value(
            cr, uid, field, value, context=context)

