# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import TransactionCase, tagged
from odoo.tools import convert_file


@tagged("-at_install", "post_install")
class TestQWebTextControl(TransactionCase):
    """Test QWeb Text Control functionality."""

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
        self.assertEqual(context["T"](0.15, 8), "00000015")

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
        test_content = "Field1<PIPE/>Field2<TAB/>Field3<LF/>Field4<CRLF/>Field5"
        processed = self.demo_report._postprocess_text(test_content)

        expected = "Field1|Field2\tField3\nField4\r\nField5"
        self.assertEqual(processed, expected)

    def test_postprocess_text_removes_line_breaks(self):
        """Test that unwanted line breaks are removed."""
        # Test content with unwanted line breaks
        test_content = "Line1\nLine2\r\nLine3\rLine4<PIPE/>Line5"
        processed = self.demo_report._postprocess_text(test_content)

        # Unwanted line breaks should be removed, special elements preserved
        self.assertNotIn("\n", processed)
        self.assertNotIn("\r", processed)
        self.assertIn("|", processed)

    def test_postprocess_text_handles_bytes(self):
        """Test that bytes input is handled correctly."""
        # Test bytes input
        test_content = b"Field1<PIPE/>Field2<CRLF/>Field3"
        processed = self.demo_report._postprocess_text(test_content)

        expected = "Field1|Field2\r\nField3"
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
        self.assertEqual(elements["PIPE"], "|")
        self.assertEqual(elements["SEMICOLON"], ";")

    def test_case_insensitive_elements(self):
        """Test that elements work case-insensitively."""
        # Test mixed case elements
        test_content = "Field1<PIPE/>field2<pipe/>Field3<LF/>field4<lf/>"
        processed = self.demo_report._postprocess_text(test_content)

        expected = "Field1|field2|Field3\nfield4\n"
        self.assertEqual(processed, expected)
