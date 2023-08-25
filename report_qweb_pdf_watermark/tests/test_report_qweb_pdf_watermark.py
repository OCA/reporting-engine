# © 2016 Therp BV <http://therp.nl>
# Copyright 2023 Onestein - Anjeel Haria
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from PIL import Image

from odoo.tests.common import HttpCase


class TestReportQwebPdfWatermark(HttpCase):
    def test_report_qweb_pdf_watermark(self):
        Image.init()
        # with our image, we have three
        self._test_report_images(3)

        self.env.ref("report_qweb_pdf_watermark.demo_report").write(
            {"pdf_watermark_expression": False}
        )
        # without, we have two
        self._test_report_images(2)

        self.env.ref("report_qweb_pdf_watermark.demo_report").write(
            {"pdf_watermark": self.env.user.company_id.logo}
        )
        # and now we should have three again
        self._test_report_images(3)

        # test use company watermark
        self.env.ref("report_qweb_pdf_watermark.demo_report").write(
            {"pdf_watermark": False}
        )
        self.env.ref("report_qweb_pdf_watermark.demo_report").write(
            {"use_company_watermark": True}
        )
        self.env.ref("base.main_company").write(
            {"pdf_watermark": self.env.user.company_id.logo}
        )
        self._test_report_images(3)

    def _test_report_images(self, number):
        pdf, _ = (
            self.env["ir.actions.report"]
            .with_context(force_report_rendering=True)
            ._render_qweb_pdf(
                "report_qweb_pdf_watermark.demo_report",
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
