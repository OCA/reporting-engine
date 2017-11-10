# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
import logging
_logger = logging.getLogger(__name__)

try:
    from xlrd import open_workbook
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class TestReport(common.TransactionCase):
    def test_report(self):
        report_object = self.env['ir.actions.report']
        report_name = 'report_xlsx.partner_xlsx'
        report = report_object._get_report_from_name(report_name)
        docs = self.env['res.company'].search([], limit=1).partner_id
        self.assertEqual(report.report_type, 'xlsx')
        rep = report.render(docs.ids, {})
        wb = open_workbook(file_contents=rep[0])
        sheet = wb.sheet_by_index(0)
        self.assertEqual(sheet.cell(0, 0).value, docs.name)
