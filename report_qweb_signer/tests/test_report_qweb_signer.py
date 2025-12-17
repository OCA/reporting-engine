# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import HttpCase


class TestReportQwebSigner(HttpCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.report = self.env.ref(
            "report_qweb_signer.partner_demo_report"
        ).with_context(force_report_rendering=True)
        self.report_ref = self.report.report_name
        self.db_cert = self.env.ref("report_qweb_signer.demo_db_certificate")

    def _assert_pdf_signed(self, pdf_bytes: bytes):
        """Very lightweight “is signed PDF” heuristics
        Note: We could add a stricter check by parsing the xref, but this keeps the test
        fast and robust.
        """
        self.assertIn(b"/ByteRange", pdf_bytes)
        self.assertIn(b"/Contents", pdf_bytes)

    def test_report_qweb_signer(self):
        content, out_ext = self.report._render_qweb_pdf(
            self.report_ref, self.partner.ids
        )
        self.assertEqual(out_ext, "pdf")
        self._assert_pdf_signed(content)
