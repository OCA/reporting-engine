# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo.tests.common import HttpCase
from odoo.tools import file_open


class TestReportQwebSigner(HttpCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        with file_open(
            "report_qweb_signer/static/certificate/test.p12", "rb"
        ) as cert_file:
            cert_content = base64.b64encode(cert_file.read())
        self.db_cert = self.env["certificate.certificate"].create(
            {
                "name": "Test Certificate Qweb",
                "content": cert_content,
                "pkcs12_password": "admin",
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.env["ir.ui.view"].create(
            {
                "name": "report_partner_test_document",
                "key": "report_qweb_signer.report_partner_test_document",
                "type": "qweb",
                "arch": """
                    <t t-call="web.external_layout">
                        <div class="page">
                            <div class="row">
                                <div class="col-md-12">
                                    <span>This is a sample report for testing PDF
                                    certificates.</span>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-12">
                                    <strong>Partner:</strong>
                                    <span t-field="o.name"/>
                                </div>
                            </div>
                        </div>
                    </t>
                """,
            }
        )
        self.env["ir.ui.view"].create(
            {
                "name": "report_partner_test",
                "key": "report_qweb_signer.report_partner_test",
                "type": "qweb",
                "arch": """
                    <t t-call="web.html_container">
                        <t t-foreach="docs" t-as="o">
                            <t t-call="report_qweb_signer.report_partner_test_document"
                               t-lang="o.lang"/>
                        </t>
                    </t>
                """,
            }
        )
        self.report = (
            self.env["ir.actions.report"]
            .create(
                {
                    "name": "Test PDF certificate",
                    "model": "res.partner",
                    "report_type": "qweb-pdf",
                    "report_name": "report_qweb_signer.report_partner_test",
                    "attachment": (
                        "'test_' + (object.name or '').replace(' ', '_').lower() "
                        "+ '.pdf'"
                    ),
                    "certificate_id": self.db_cert.id,
                    "signed_attachment": (
                        "'test_' + (object.name or '').replace(' ', '_').lower() "
                        "+ '.signed.pdf'"
                    ),
                    "attachment_use": True,
                    "signing_allow_only_one": True,
                }
            )
            .with_context(force_report_rendering=True)
        )
        self.report_ref = self.report.report_name

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
