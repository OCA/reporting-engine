# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import HttpCase


class TestReportQwebSigner(HttpCase):
    def setUp(self):
        super(TestReportQwebSigner, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': 'Test partner',
            'customer': True,
        })
        self.report = self.env.ref('report_qweb_signer.partner_demo_report')

    def test_report_qweb_signer(self):
        self.report.render_qweb_pdf(self.partner.ids)
        # Reprint again for taking the PDF from attachment
        self.report.render_qweb_pdf(self.partner.ids)
