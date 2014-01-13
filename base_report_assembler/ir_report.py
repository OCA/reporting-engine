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
from openerp.osv import orm
from openerp import netsvc
from openerp.report.report_sxw import rml_parse
from report_assembler import PDFReportAssembler


def register_report(name, model, parser=rml_parse):
    """ Register the report into the services """
    name = 'report.%s' % name
    if netsvc.Service._services.get(name, False):
        service = netsvc.Service._services[name]
        if isinstance(service, PDFReportAssembler):
            #already instantiated properly, skip it
            return
        if hasattr(service, 'parser'):
            parser = service.parser
        del netsvc.Service._services[name]
    PDFReportAssembler(name, model, parser=parser)


class ReportAssembleXML(orm.Model):

    _name = 'ir.actions.report.xml'
    _inherit = 'ir.actions.report.xml'

    def __init__(self, pool, cr):
        super(ReportAssembleXML, self).__init__(pool, cr)

    def register_all(self, cursor):
        value = super(ReportAssembleXML, self).register_all(cursor)
        cursor.execute("SELECT * FROM ir_act_report_xml WHERE report_type = 'assemblage'")
        records = cursor.dictfetchall()
        for record in records:
            register_report(record['report_name'], record['model'])
        return value

    def unlink(self, cursor, user, ids, context=None):
        """ Delete report and unregister it """
        trans_obj = self.pool.get('ir.translation')
        trans_ids = trans_obj.search(
            cursor,
            user,
            [('type', '=', 'report'), ('res_id', 'in', ids)]
            )
        trans_obj.unlink(cursor, user, trans_ids)

        # Warning: we cannot unregister the services at the moment
        # because they are shared across databases. Calling a deleted
        # report will fail so it's ok.

        res = super(ReportAssembleXML, self).unlink(
            cursor,
            user,
            ids,
            context)
        return res

    def create(self, cursor, user, vals, context=None):
        """ Create report and register it """
        res = super(ReportAssembleXML, self).create(cursor, user, vals, context)
        if vals.get('report_type', '') == 'assemblage':
            # I really look forward to virtual functions :S
            register_report(
                vals['report_name'],
                vals['model'])
        return res

    def write(self, cr, uid, ids, vals, context=None):
        """ Edit report and manage its registration """
        if isinstance(ids, (int, long)):
            ids = [ids]
        for rep in self.browse(cr, uid, ids, context=context):
            if rep.report_type != 'assemblage':
                continue
            if (vals.get('report_name', False)
                    and vals['report_name'] != rep.report_name):
                report_name = vals['report_name']
            else:
                report_name = rep.report_name

            register_report(
                report_name,
                vals.get('model', rep.model),
                False
                )
        res = super(ReportAssembleXML, self).write(cr, uid, ids, vals, context)
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
