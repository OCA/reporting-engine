# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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
from openerp.osv import orm, fields

class AssembledReport(orm.Model):
    _name = 'assembled.report'

    _order = 'sequence'

    _columns = {
        'report_id': fields.many2one(
            'ir.actions.report.xml', 'Report',
            domain="[('model', '=', model),"
                   "('report_type', '!=', 'assemblage')]", required=True),
        'model': fields.char('Object model'),
        'sequence': fields.integer('Sequence', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        }

    _defaults = {
        'sequence': 1,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(
            cr, uid, 'assembled.report', context=c)
        }
