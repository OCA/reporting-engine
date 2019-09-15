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
        self.report = self.env.ref(
            'report_qweb_signer.partner_demo_report'
        ).with_context(force_report_rendering=True)

    def test_report_qweb_signer(self):
        self.report.render_qweb_pdf(self.partner.ids)
        # Reprint again for taking the PDF from attachment
        IrAttachment = self.env['ir.attachment']
        domain = [
            ('res_id', '=', self.partner.id),
            ('res_model', '=', self.partner._name),
        ]
        num_attachments = IrAttachment.search_count(domain)
        self.report.render_qweb_pdf(self.partner.ids)
        num_attachments_after = IrAttachment.search_count(domain)
        self.assertEqual(num_attachments, num_attachments_after)
