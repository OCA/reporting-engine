# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestReport(common.TransactionCase):
    def test_report(self):
        report_object = self.env['ir.actions.report']
        report_name = 'report_fillpdf.partner_fillpdf'
        report = report_object._get_report_from_name(report_name)
        docs = self.env['res.company'].search([], limit=1).partner_id
        self.assertEqual(report.report_type, 'fillpdf')
        report.render(docs.ids, {})
