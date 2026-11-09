# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime

from odoo.tests import TransactionCase, tagged
from odoo.tools import convert_file


@tagged("-at_install", "post_install")
class TestReportIntegration(TransactionCase):
    """Test report integration with demo report."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Load demo report data
        convert_file(
            cls.env,
            module="report_qweb_text_control",
            filename="demo/partner_report.xml",
            idref={},
            mode="init",
            noupdate=True,
        )
        cls.demo_report = cls.env.ref(
            "report_qweb_text_control.action_report_partner_text"
        )

    def setUp(self):
        super().setUp()
        # Create test partner
        self.test_partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
                "phone": "+1234567890",
                "company_type": "company",
                "partner_latitude": 41.1579,
                "country_id": self.env.ref("base.us").id,
            }
        )

    def _get_rendering_context(self, report=None, docids=None):
        report = report or self.demo_report
        docids = docids or [self.test_partner.id]
        return self.env["ir.actions.report"]._get_rendering_context(report, docids, {})

    def test_field_formatters_in_context(self):
        """Test that field formatters are available in render context."""
        context = self._get_rendering_context()

        # Test formatter functions
        self.assertEqual(context["A"]("Test", 10), "Test      ")
        self.assertEqual(context["N"](123, 8), "00000123")
        self.assertEqual(context["M"](100.50, 10), "000010050+")
        test_date = datetime(2025, 1, 15)
        self.assertEqual(context["D"](test_date), "20250115")
        test_datetime = datetime(2025, 1, 15, 14, 30, 45)
        self.assertEqual(context["H"](test_datetime), "1430")
        # Tax formatter with default length=5
        self.assertEqual(context["T"](123.45), "12345")
        self.assertEqual(context["DT"](test_datetime), "202501151430")

    def test_report_rendering(self):
        """Test that the report renders correctly with post-processing."""
        # Render the report
        content, format_type = self.env["ir.actions.report"]._render_qweb_text(
            self.demo_report, [self.test_partner.id]
        )

        # Check format type
        self.assertEqual(format_type, "text")

        # Check that content is bytes and decodes to a string
        self.assertIsInstance(content, bytes)
        text = content.decode("utf-8")

        # Check that special elements are replaced
        self.assertIn("\r\n", text)  # CRLF elements

        # Check that field formatting works
        self.assertIn("Test Partner", text)
        self.assertIn("test@example.com", text)
        self.assertIn("+1234567890", text)
        self.assertIn("United States", text)
        self.assertIn("0010000+", text)  # Company monetary format
        self.assertIn("00000004116+", text)  # Partner latitude with sign

    def test_postprocess_text_replacement_elements(self):
        """Test text post-processing with replacement elements."""
        # Test content with various special elements
        test_content = "Field1<TAB/>Field2<CRLF/>Field3<SEMICOLON/>Field4"
        processed = self.demo_report._postprocess_text(test_content)

        expected = "Field1\tField2\r\nField3;Field4"
        self.assertEqual(processed, expected)

    def test_postprocess_text_removes_line_breaks(self):
        """Test that unwanted line breaks are removed."""
        # Test content with unwanted line breaks
        test_content = "Line1\nLine2\r\nLine3\rLine4\nLine5"
        processed = self.demo_report._postprocess_text(test_content)

        # Unwanted line breaks should be removed, special elements preserved
        self.assertNotIn("\n", processed)
        self.assertNotIn("\r", processed)

    def test_postprocess_text_handles_bytes(self):
        """Test that bytes input is handled correctly."""
        # Test bytes input
        test_content = b"Field1<TAB/>Field2<CRLF/>Field3"
        processed = self.demo_report._postprocess_text(test_content)

        expected = "Field1\tField2\r\nField3"
        self.assertEqual(processed, expected)

    def test_replacement_elements_configuration(self):
        """Test that replacement elements can be customized."""
        # Get default replacement elements
        elements = self.demo_report._get_replacement_elements()

        # Check default elements
        self.assertEqual(elements["CR"], "\r")
        self.assertEqual(elements["LF"], "\n")
        self.assertEqual(elements["CRLF"], "\r\n")
        self.assertEqual(elements["TAB"], "\t")
        self.assertEqual(elements["SEMICOLON"], ";")

    def test_case_insensitive_elements(self):
        """Test that elements work case-insensitively."""
        # Test mixed case elements
        test_content = "Field1<TAB/>field2<tab/>Field3<CR/>field4<cr/>"
        processed = self.demo_report._postprocess_text(test_content)

        expected = "Field1\tfield2\tField3\rfield4\r"
        self.assertEqual(processed, expected)

    def test_regular_text_report_no_formatters(self):
        """
        Test that regular text reports don't have field formatters
        when text control is disabled.
        """
        # Create a regular text report with text control disabled
        regular_report = self.env["ir.actions.report"].create(
            {
                "name": "Regular Text Report",
                "model": "res.partner",
                "report_type": "qweb-text",
                "report_name": "test_regular_text_report",
                "text_control_enabled": False,
            }
        )

        # Get rendering context - should not have field formatters
        context = self._get_rendering_context(report=regular_report)

        # Field formatters should not be available
        self.assertNotIn("A", context)
        self.assertNotIn("N", context)
        self.assertNotIn("DT", context)
