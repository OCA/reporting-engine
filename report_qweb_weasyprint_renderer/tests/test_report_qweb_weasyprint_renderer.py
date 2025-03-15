# Copyright 2025 Hunki Enterprises BV <https://hunki-enterprises.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestReportQwebWeasyprintRenderer(TransactionCase):
    def test_report_qweb_weasyprint_renderer(self):
        for xmlid in (
            "demo_report_external_layout",
            "demo_report_internal_layout",
            "demo_report_html_wrapper",
            "demo_report_custom",
        ):

            pdf, file_type = self.env["ir.actions.report"]._render(
                "report_qweb_weasyprint_renderer.%s" % xmlid,
                self.env["ir.module.module"].search([("application", "=", True)]).ids,
            )
            self.assertEqual(file_type, "pdf")
            self.assertTrue(pdf.startswith(b"%PDF"))
