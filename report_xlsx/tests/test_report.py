# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests import common

_logger = logging.getLogger(__name__)

try:
    from xlrd import open_workbook
except ImportError:
    _logger.debug("Can not import xlrd`.")


class TestReport(common.TransactionCase):
    def setUp(self):
        super(TestReport, self).setUp()
        report_object = self.env["ir.actions.report"]
        self.xlsx_report = self.env["report.report_xlsx.abstract"].with_context(
            active_model="res.partner"
        )
        self.report_name = "report_xlsx.partner_xlsx"
        self.report = report_object._get_report_from_name(self.report_name)
        self.docs = self.env["res.company"].search([], limit=1).partner_id

    def test_report(self):
        report = self.report
        self.assertEqual(report.report_type, "xlsx")
        rep = report._render(self.docs.ids, {})
        wb = open_workbook(file_contents=rep[0])
        sheet = wb.sheet_by_index(0)
        self.assertEqual(sheet.cell(0, 0).value, self.docs.name)

    def test_id_retrieval(self):

        # Typical call from WebUI with wizard
        objs = self.xlsx_report._get_objs_for_report(
            False, {"context": {"active_ids": self.docs.ids}}
        )
        self.assertEqual(objs, self.docs)

        # Typical call from within code not to report_action
        objs = self.xlsx_report.with_context(
            active_ids=self.docs.ids
        )._get_objs_for_report(False, False)
        self.assertEqual(objs, self.docs)

        # Typical call from WebUI
        objs = self.xlsx_report._get_objs_for_report(
            self.docs.ids, {"data": [self.report_name, self.report.report_type]}
        )
        self.assertEqual(objs, self.docs)

        # Typical call from render
        objs = self.xlsx_report._get_objs_for_report(self.docs.ids, {})
        self.assertEqual(objs, self.docs)
