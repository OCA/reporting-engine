# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import HttpCase


class TestReportKeepLatestAttachment(HttpCase):
    def setUp(self):
        super(TestReportKeepLatestAttachment, self).setUp()

        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.report = self.env.ref(
            "report_keep_latest_attachment.action_keep_latest_attachment_report"
        ).with_context(force_report_rendering=True)

    def test_report_keep_latest_attachment(self):
        IrAttachment = self.env["ir.attachment"]
        domain = [
            ("res_model", "=", self.partner._name),
            ("res_id", "=", str(self.partner.id)),
            ("name", "ilike", "%{}%".format(self.partner.name)),
        ]

        # First we check if field keep_latest_attachment is set to False
        self.assertFalse(self.report.keep_latest_attachment)

        # Attachments should not exist
        num_attachments = IrAttachment.search_count(domain)
        self.assertFalse(num_attachments)

        # Generate first report attachment
        self.report._render_qweb_pdf(self.partner.ids)
        num_attachments = IrAttachment.search(domain)
        self.assertTrue(num_attachments)
        self.assertEqual(len(num_attachments), 1)

        # Duplicate Attachment, If using send_mail; this will be attached if
        # report_template field is set on mail_template.

        IrAttachment.create(
            {
                "name": "%s.pdf" % self.partner.name,
                "type": "binary",
                "datas": num_attachments.datas,
                "res_model": num_attachments.res_model,
                "res_id": num_attachments.res_id,
            }
        )
        num_attachments = IrAttachment.search_count(domain)
        self.assertTrue(num_attachments)
        self.assertEqual(num_attachments, 2)

        # Now we set report to keep only latest generate attachment report
        self.report.keep_latest_attachment = True
        self.report._render_qweb_pdf(self.partner.ids)
        num_attachments = IrAttachment.search_count(domain)
        self.assertTrue(num_attachments)

        # should be only one attachment; the latest attachment
        self.assertEqual(num_attachments, 1)
