# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class TestReportQwebSigner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestReportQwebSigner, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'customer': True,
        })
        cls.report = cls.env.ref('report_qweb_signer.partner_demo_report')

    def test_report_qweb_signer(self):
        self.env['report'].get_pdf(
            self.partner.ids, self.report.report_name, data={},
        )
        # Reprint again for taking the PDF from attachment
        self.env['report'].get_pdf(
            self.partner.ids, self.report.report_name, data={},
        )
