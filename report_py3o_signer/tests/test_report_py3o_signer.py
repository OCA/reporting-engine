# Copyright 2023 fah-mili/Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestReportPy3oSignerCase(TransactionCase):
    def setUp(self):
        super(TestReportPy3oSignerCase, self).setUp()
        self.user = self.env.ref('base.user_admin')
        self.report = self.env.ref(
            'report_py3o.res_users_report_py3o'
        ).with_context(force_report_rendering=True)
        self.report.py3o_filetype = 'pdf'
        self.report.attachment_use = True
        self.report.attachment = "'test_' + (object.name or '') + '.pdf'"

        user_model = self.env['ir.model'].search([('model', '=', 'res.users')])
        self.certificate = self.env.ref('report_qweb_signer.demo_certificate_test')
        self.certificate.model_id = user_model
        self.certificate.domain = "[]"


class TestReportPy3oSigner(TestReportPy3oSignerCase):
    def test_report_py3o_signer(self):
        user_ids = self.user.ids
        self.report.render_py3o(user_ids)
        # we should find the saved signed content
        signed_content = self.report._attach_signed_read(user_ids, self.certificate)
        self.assertTrue(signed_content)

        # Reprint again for taking the PDF from attachment
        IrAttachment = self.env['ir.attachment']
        domain = [
            ('res_id', '=', self.user.id),
            ('res_model', '=', self.user._name),
        ]
        num_attachments = IrAttachment.search_count(domain)
        self.report.render_py3o(user_ids)
        num_attachments_after = IrAttachment.search_count(domain)
        self.assertEqual(num_attachments, num_attachments_after)
