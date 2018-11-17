# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestReportQwebWeasyprintRenderer(TransactionCase):
    def test_report_qweb_weasyprint_renderer(self):
        pdf, file_type = self.env.ref(
            'report_qweb_weasyprint_renderer.demo_report'
        ).render(self.env['res.company'].search([]).ids)
        self.assertEqual(file_type, 'pdf')
        self.assertTrue(pdf.startswith(b'%PDF'))
