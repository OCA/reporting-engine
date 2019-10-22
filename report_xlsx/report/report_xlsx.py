# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from cStringIO import StringIO

from odoo.report.report_sxw import report_sxw
from odoo.api import Environment

import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class ReportXlsx(report_sxw):

    def create(self, cr, uid, ids, data, context=None):
        self.env = Environment(cr, uid, context)
        report_obj = self.env['ir.actions.report.xml']
        report = report_obj.search([('report_name', '=', self.name[7:])])
        if report.ids:
            self.title = report.name
            if report.report_type == 'xlsx':
                return self.create_xlsx_report(ids, data, report)
        return super(ReportXlsx, self).create(cr, uid, ids, data, context)

    def create_workbook(self, file_data, data, objs, report):
        workbook = xlsxwriter.Workbook(file_data, self.get_workbook_options())
        self.generate_xlsx_report(workbook, data, objs)
        for sheet in workbook.worksheets():
            if report and report.header_id and report.header_id.value:
                sheet.set_header(report.header_id.value,
                                 report.header_id.get_options())
            if report and report.footer_id and report.footer_id.value:
                sheet.set_footer(report.footer_id.value,
                                 report.footer_id.get_options())
        return workbook

    def create_xlsx_report(self, ids, data, report):
        self.parser_instance = self.parser(
            self.env.cr, self.env.uid, self.name2, self.env.context)
        objs = self.getObjects(
            self.env.cr, self.env.uid, ids, self.env.context)
        self.parser_instance.set_context(objs, data, ids, 'xlsx')
        file_data = StringIO()
        workbook = self.create_workbook(file_data, data, objs, report)
        workbook.close()
        file_data.seek(0)
        return (file_data.read(), 'xlsx')

    def get_workbook_options(self):
        return {}

    def generate_xlsx_report(self, workbook, data, objs):
        raise NotImplementedError()
