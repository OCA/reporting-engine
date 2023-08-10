# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests.common import HttpCase


class TestReportQwebEncrypt(HttpCase):
    def test_report_qweb_no_encrypt(self):
        ctx = {"force_report_rendering": True}
        report = self.env.ref("web.action_report_internalpreview")
        report.encrypt = False
        pdf, _ = report.with_context(**ctx)._render_qweb_pdf(report.report_name, [1])
        self.assertFalse(pdf.count(b"/Encrypt"))

    def test_report_qweb_auto_encrypt(self):
        ctx = {"force_report_rendering": True}
        report = self.env.ref("web.action_report_internalpreview")
        report.encrypt = "auto"
        report.encrypt_password = False

        # If no encrypt_password, still not encrypted
        pdf, _ = report.with_context(**ctx)._render_qweb_pdf(report.report_name, [1])
        self.assertFalse(pdf.count(b"/Encrypt"))

        # If invalid encrypt_password, show error
        report.encrypt_password = "invalid python syntax"
        with self.assertRaises(ValidationError):
            pdf, _ = report.with_context(**ctx)._render_qweb_pdf(
                report.report_name, [1]
            )

        # Valid python string for password
        report.encrypt_password = "'secretcode'"
        pdf, _ = report.with_context(**ctx)._render_qweb_pdf(report.report_name, [1])
        self.assertTrue(pdf.count(b"/Encrypt"))

    def test_report_qweb_manual_encrypt(self):
        ctx = {"force_report_rendering": True}
        report = self.env.ref("web.action_report_internalpreview")
        report.encrypt = "manual"

        # If no encrypt_password, still not encrypted
        pdf, _ = report.with_context(**ctx)._render_qweb_pdf(report.report_name, [1])
        self.assertFalse(pdf.count(b"/Encrypt"))

        # Valid python string for password
        ctx.update({"encrypt_password": "secretcode"})
        pdf, _ = report.with_context(**ctx)._render_qweb_pdf(report.report_name, [1])
        self.assertTrue(pdf.count(b"/Encrypt"))

    # TODO: test_report_qweb_manual_encrypt, require JS test?
