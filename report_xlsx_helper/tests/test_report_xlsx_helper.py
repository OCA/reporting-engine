# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestReportXlsxHelper(TransactionCase):

    def setUp(self):
        super(TestReportXlsxHelper, self).setUp()
        ctx = {'xlsx_export': True}
        self.report = self.env['ir.actions.report.xml'].with_context(ctx)
        self.report_name = 'test.partner.xlsx'
        p1 = self.env.ref('base.res_partner_1')
        p2 = self.env.ref('base.res_partner_2')
        self.partners = p1 + p2

    def test_report_xlsx_helper(self):
        report_xls = self.report.render_report(
            self.partners.ids, self.report_name, {})
        self.assertEqual(report_xls[1], 'xlsx')
