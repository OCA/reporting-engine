# © 2016 Therp BV <http://therp.nl>
# Copyright 2023 Onestein - Anjeel Haria
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from PIL import Image

from odoo.tests.common import HttpCase
from odoo.tools.binary import BinaryBytes


class TestReportQwebPdfWatermark(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Create test report template programmatically
        cls.env["ir.ui.view"].create(
            {
                "name": "Test Watermark Report Template",
                "type": "qweb",
                "key": "report_qweb_pdf_watermark.test_report_view",
                "arch": """
                <t t-name="report_qweb_pdf_watermark.test_report_view">
                    <t t-call="web.html_container">
                        <t t-call="web.external_layout">
                            <div class="page">
                                <ul>
                                    <li t-foreach="docs" t-as="doc">
                                        <t t-out="doc.name" />
                                    </li>
                                </ul>
                            </div>
                        </t>
                    </t>
                </t>
            """,
            }
        )

        # Create test report action
        cls.test_report = cls.env["ir.actions.report"].create(
            {
                "name": "Test Watermark Report",
                "model": "res.users",
                "report_type": "qweb-pdf",
                "report_name": "report_qweb_pdf_watermark.test_report_view",
                "pdf_watermark_expression": "docs[:1].company_id.logo",
            }
        )

        logo1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk"
        logo2 = "+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        # Ensure company has a logo for testing
        if not cls.env.user.company_id.logo:
            # Create a minimal test logo (1x1 transparent PNG)
            cls.env.user.company_id.logo = logo1 + logo2

    def test_report_qweb_pdf_watermark(self):
        Image.init()
        # with our image, we have three
        self._test_report_images(3)

        self.test_report.write({"pdf_watermark_expression": False})
        # without, we have two
        self._test_report_images(2)

        self.test_report.write({"pdf_watermark": self.env.user.company_id.logo})
        # and now we should have three again
        self._test_report_images(3)

        # test use company watermark
        self.test_report.write({"pdf_watermark": False})
        self.test_report.write({"use_company_watermark": True})
        self.env.user.company_id.write({"pdf_watermark": self.env.user.company_id.logo})
        self._test_report_images(3)

    def test_report_attachment_not_watermarked_twice(self):
        """A report reloaded from its saved attachment keeps one watermark"""
        self.env["ir.ui.view"].create(
            {
                "name": "Test Watermark Attachment Template",
                "type": "qweb",
                "key": "report_qweb_pdf_watermark.test_report_attachment_view",
                "arch": """
                <t t-name="report_qweb_pdf_watermark.test_report_attachment_view">
                    <t t-call="web.html_container">
                        <t t-foreach="docs" t-as="doc">
                            <t t-call="web.external_layout">
                                <div class="page"><span t-out="doc.name" /></div>
                            </t>
                        </t>
                    </t>
                </t>
            """,
            }
        )
        report = self.env["ir.actions.report"].create(
            {
                "name": "Test Watermark Attachment Report",
                "model": "res.users",
                "report_type": "qweb-pdf",
                "report_name": "report_qweb_pdf_watermark.test_report_attachment_view",
                "pdf_watermark_expression": "docs[:1].company_id.logo",
                "attachment": "'watermark-%s.pdf' % object.id",
                "attachment_use": True,
            }
        )
        Report = self.env["ir.actions.report"].with_context(force_report_rendering=True)
        user = self.env.user
        first, _ = Report._render_qweb_pdf(report.report_name, user.ids)
        self.assertTrue(
            self.env["ir.attachment"].search(
                [
                    ("res_model", "=", "res.users"),
                    ("res_id", "=", user.id),
                    ("name", "=", f"watermark-{user.id}.pdf"),
                ]
            )
        )
        # The second print is reloaded from the attachment
        second, _ = Report._render_qweb_pdf(report.report_name, user.ids)
        self.assertEqual(
            second.count(b"/Subtype /Image"), first.count(b"/Subtype /Image")
        )

    def _test_report_images(self, number):
        pdf, _ = (
            self.env["ir.actions.report"]
            .with_context(force_report_rendering=True)
            ._render_qweb_pdf(
                self.test_report.report_name,
                self.env["res.users"].search([]).ids,
            )
        )
        self.assertEqual(pdf.count(b"/Subtype /Image"), number)

    def test_company_watermark_uses_document_company(self):
        company_b = self.env["res.company"].create(
            {
                "name": "Watermark Company B",
                "pdf_watermark": BinaryBytes(b"watermark-b"),
            }
        )
        partner = self.env["res.partner"].create(
            {"name": "Watermark Partner", "company_id": company_b.id}
        )
        report = self.test_report.copy(
            {"model": "res.partner", "use_company_watermark": True}
        )
        Report = self.env["ir.actions.report"]
        self.assertEqual(Report._get_watermark(partner.ids, report), b"watermark-b")
        # Without documents, the current company is used
        self.env.company.pdf_watermark = BinaryBytes(b"watermark-a")
        self.assertEqual(Report._get_watermark([], report), b"watermark-a")

    def test_raw_report_uses_original_watermark(self):
        self.test_report.write(
            {
                "pdf_watermark_expression": False,
                "pdf_watermark": BinaryBytes(b"watermark-orig"),
            }
        )
        raw_report = self.test_report.copy(
            {
                "report_name": f"{self.test_report.report_name}_raw",
                "pdf_watermark": False,
            }
        )
        Report = self.env["ir.actions.report"]
        self.assertEqual(
            Report._get_watermark(self.env.user.ids, raw_report), b"watermark-orig"
        )

    def test_pdf_has_usable_pages(self):
        # test 0
        numpages = 0
        # pdf_has_usable_pages(self, pdf_watermark)
        with self.assertLogs(level="ERROR"):
            self.assertFalse(
                self.env["ir.actions.report"].pdf_has_usable_pages(numpages)
            )
        # test 1
        numpages = 1
        self.assertTrue(self.env["ir.actions.report"].pdf_has_usable_pages(numpages))
        # test 2
        numpages = 2
        self.assertTrue(self.env["ir.actions.report"].pdf_has_usable_pages(numpages))
