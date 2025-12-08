# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import TransactionCase, tagged
from odoo.tools.convert import xml_import


@tagged("-at_install", "post_install")
class TestQWebTextControl(TransactionCase):
    """Test QWeb Text Control functionality."""

    def setUp(self):
        super().setUp()
        # Load demo report data using Odoo's XML import
        self._load_demo_report()

        # Create test partner
        self.test_partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
                "phone": "+1234567890",
                "company_type": "company",
                "credit_limit": 1500.50,
                "country_id": self.env.ref("base.us").id,
            }
        )

    def _load_demo_report(self):
        """Load demo report data using Odoo's XML import utility."""
        # Use Odoo's xml_import to load the demo data
        xml_import(
            self.env.cr,
            "report_qweb_text_control",
            "report_qweb_text_control/demo/partner_report.xml",
            mode="init",
            noupdate=True,
        )

        # Get the demo report that was created
        self.demo_report = self.env.ref(
            "report_qweb_text_control.action_report_partner_text"
        )

    def test_field_formatters_in_context(self):
        """Test that field formatters are available in render context."""
        report = self.demo_report
        context = report._get_rendering_context([self.test_partner.id], {})
        # Test formatter functions
        self.assertEqual(context["A"]("Test", 10), "Test      ")
        self.assertEqual(context["N"](123, 8), "00000123")
        self.assertEqual(context["M"](100.50, 10), "0000010050+")
        self.assertEqual(context["T"](0.15, 8), "00000150")

    def test_report_rendering(self):
        """Test that the report renders correctly with post-processing."""
        report = self.demo_report

        # Render the report
        content, format_type = report._render_qweb_text([self.test_partner.id])

        # Check format type
        self.assertEqual(format_type, "text")

        # Check that content is a string
        self.assertIsInstance(content, str)

        # Check that special elements are replaced
        self.assertIn("|", content)  # PIPE elements
        self.assertIn("\r\n", content)  # CRLF elements

        # Check that field formatting works
        self.assertIn("Test Partner", content)
        self.assertIn("test@example.com", content)
        self.assertIn("+1234567890", content)
        self.assertIn("United States", content)
        self.assertIn("00000100+", content)  # Company monetary format
        self.assertIn("0000150050+", content)  # Credit limit with sign

    def test_postprocess_text_replacement_elements(self):
        """Test text post-processing with replacement elements."""
        report = self.demo_report

        # Test content with various special elements
        test_content = "Field1<PIPE/>Field2<TAB/>Field3<LF/>Field4<CRLF/>Field5"
        processed = report._postprocess_text(test_content)

        expected = "Field1|Field2\tField3Field4\r\nField5"
        self.assertEqual(processed, expected)

    def test_postprocess_text_removes_line_breaks(self):
        """Test that unwanted line breaks are removed."""
        report = self.demo_report

        # Test content with unwanted line breaks
        test_content = "Line1\nLine2\r\nLine3\rLine4<PIPE/>Line5"
        processed = report._postprocess_text(test_content)

        # Unwanted line breaks should be removed, special elements preserved
        self.assertNotIn("\n", processed)
        self.assertNotIn("\r", processed)
        self.assertIn("|", processed)

    def test_postprocess_text_handles_bytes(self):
        """Test that bytes input is handled correctly."""
        report = self.demo_report

        # Test bytes input
        test_content = b"Field1<PIPE/>Field2<CRLF/>Field3"
        processed = report._postprocess_text(test_content)

        expected = "Field1|Field2\r\nField3"
        self.assertEqual(processed, expected)

    def test_replacement_elements_configuration(self):
        """Test that replacement elements can be customized."""
        report = self.demo_report

        # Get default replacement elements
        elements = report._get_replacement_elements()

        # Check default elements
        self.assertEqual(elements["CR"], "\r")
        self.assertEqual(elements["LF"], "\n")
        self.assertEqual(elements["CRLF"], "\r\n")
        self.assertEqual(elements["TAB"], "\t")
        self.assertEqual(elements["PIPE"], "|")
        self.assertEqual(elements["SEMICOLON"], ";")

    def test_case_insensitive_elements(self):
        """Test that elements work case-insensitively."""
        report = self.demo_report

        # Test mixed case elements
        test_content = "Field1<PIPE/>field2<pipe/>Field3<LF/>field4<lf/>"
        processed = report._postprocess_text(test_content)

        expected = "Field1|field2|Field3field4"
        self.assertEqual(processed, expected)
