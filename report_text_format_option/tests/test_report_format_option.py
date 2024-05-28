# Copyright 2024 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).


from odoo.tests.common import TransactionCase


class TestReportFormatOption(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestReportFormatOption, cls).setUpClass()
        cls.demo_report = cls.env.ref(
            "report_text_format_option.action_report_demo"
        ).with_context(lang="en_US")
        cls.partner = cls.env["res.partner"].create({"name": "Odoo Test Partner"})

    def test_report_default_encoding(self):
        content, content_type = self.demo_report._render_qweb_text(
            self.demo_report.id, [self.partner.id]
        )
        self.assertTrue(content, "Report content should not be empty")

    def test_report_encoding_crlf(self):
        # Set line ending to CRLF
        self.demo_report.line_ending = "crlf"
        content, content_type = self.demo_report._render_qweb_text(
            self.demo_report.id, [self.partner.id]
        )
        content_str = content.decode("utf-8")
        self.assertIn("\r\n", content_str, "Line endings should be CRLF")

    def test_report_encoding_cr(self):
        # Set line ending to CR
        self.demo_report.line_ending = "cr"
        content, content_type = self.demo_report._render_qweb_text(
            self.demo_report.id, [self.partner.id]
        )
        content_str = content.decode("utf-8")
        self.assertIn("\r", content_str, "Line endings should be CR and not contain LF")

    def test_report_encoding_shiftjis(self):
        # Example: Testing with Shift-JIS encoding for Japanese characters
        self.demo_report.text_encoding = "shift_jis"
        self.partner.name = "テストパートナー"
        content, content_type = self.demo_report._render_qweb_text(
            self.demo_report.id, [self.partner.id]
        )
        # Decode content to verify Japanese characters are correctly handled
        content_str = content.decode("shift_jis")
        self.assertIn(
            "テストパートナー",
            content_str,
            "Japanese characters should be correctly encoded in Shift-JIS",
        )
