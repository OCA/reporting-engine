# © 2016 Therp BV <http://therp.nl>
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

    def _test_report_images(self, number):
        report = self.env["ir.model.data"].xmlid_to_object(
            "report_qweb_pdf_watermark.demo_report"
        )
        pdf, _ = report.with_context(force_report_rendering=True)._render_qweb_pdf(
            self.env["res.users"].search([]).ids
        )
        self.assertEqual(pdf.count(b"/Subtype /Image"), number)
