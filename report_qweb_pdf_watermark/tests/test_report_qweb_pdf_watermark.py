# © 2016 Therp BV <http://therp.nl>
# Copyright 2023 Onestein - Anjeel Haria
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from PIL import Image

from odoo import Command
from odoo.tests.common import HttpCase, TransactionCase, tagged


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
                                        <t t-esc="doc.name" />
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
            cls.env.user.company_id.logo = b"".join([logo1.encode(), logo2.encode()])

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


# post_install, so that auto-installed modules such as iap are available
@tagged("post_install", "-at_install")
class TestReportQwebPdfWatermarkCompany(TransactionCase):
    def _create_report(self, model):
        return self.env["ir.actions.report"].create(
            {
                "name": f"Test Watermark Report {model}",
                "model": model,
                "report_type": "qweb-pdf",
                "report_name": "report_qweb_pdf_watermark.test_report_view",
            }
        )

    def test_get_watermark_company(self):
        other_company = self.env["res.company"].create({"name": "Watermark Co"})
        self.assertNotEqual(self.env.company, other_company)
        report = self._create_report("res.partner")
        partner = self.env["res.partner"].create(
            {"name": "Partner", "company_id": other_company.id}
        )
        shared_partner = self.env["res.partner"].create({"name": "Shared"})

        # no documents: company from the environment
        self.assertEqual(report._get_watermark_company([], report), self.env.company)
        # document company_id wins over the environment company
        self.assertEqual(
            report._get_watermark_company(partner.ids, report), other_company
        )
        # the first document carrying a company is used
        self.assertEqual(
            report._get_watermark_company((shared_partner | partner).ids, report),
            other_company,
        )
        # document without a company: company from the environment
        self.assertEqual(
            report._get_watermark_company(shared_partner.ids, report),
            self.env.company,
        )

    def test_get_watermark_company_ids(self):
        # iap.account only has company_ids; iap is auto-installed with web
        if "iap.account" not in self.env:
            self.skipTest("iap is not installed")
        other_company = self.env["res.company"].create({"name": "Watermark Co"})
        report = self._create_report("iap.account")
        service = self.env["iap.service"].create(
            {
                "name": "Watermark",
                "technical_name": "report_qweb_pdf_watermark_test",
                "description": "Watermark test service",
                "unit_name": "Credits",
                "integer_balance": True,
            }
        )
        account = self.env["iap.account"].create(
            {
                "service_id": service.id,
                "company_ids": [Command.set(other_company.ids)],
            }
        )
        self.assertEqual(
            report._get_watermark_company(account.ids, report), other_company
        )
