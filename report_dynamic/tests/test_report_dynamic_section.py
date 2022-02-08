# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests import common


class TestWizardReportDynamicSection(common.TransactionCase):
    def setUp(self):
        super(TestWizardReportDynamicSection, self).setUp()
        # use the demodata.
        self.RD_template = self.env.ref("report_dynamic.demo_report_2")
        self.section1 = self.env.ref("report_dynamic.demo_section_1")
        # Black -> White alias
        self.alias = self.env.ref("report_dynamic.demo_alias_1")

    def test_section_count(self):
        self.assertFalse(self.RD_template.section_count)
        self.env["report.dynamic.section"].create({"report_id": self.RD_template.id})
        self.assertEqual(self.RD_template.section_count, 1)

    def test_condition_python_preview(self):
        self.assertEqual(self.section1.condition_python, 'object.name.startswith("D")')
        self.assertFalse(self.section1.condition_python_preview)
        # Evaluate condition to true
        # Selected partner record is 'Wood Corner'
        self.section1.condition_python = 'object.name.startswith("W")'
        # trigger the computation for preview
        self.section1._compute_condition_python_preview()
        # an empty python_condition evaluates to string True
        self.assertEqual(self.section1.condition_python_preview, "True")
        # Check for syntax errors
        self.section1.condition_python = 'object_name.startswith("D")'
        self.section1._compute_condition_python_preview()
        # read preview
        self.assertEqual(
            self.section1.condition_python_preview,
            "<class 'NameError'>: "
            "\"name 'object_name' is not defined"
            '" while evaluating\n\'object_name.startswith("D")\'',
        )
        # nullify condition python
        self.section1.condition_python = False
        self.section1._compute_condition_python_preview()
        self.assertEqual(self.section1.condition_python_preview, "True")
        # Finally, check that preview gets False if there's no record
        self.section1.resource_ref = False
        self.section1._compute_condition_python_preview()
        self.assertFalse(self.section1.condition_python_preview)

    def test_compute_dynamic_content(self):
        self.assertFalse(self.section1.dynamic_content)
        self.section1.condition_python = 'object.name.startswith("W")'
        self.alias.active = False
        self.assertEqual(self.section1.content, "<p>Some Black content</p>")
        self.alias.active = True
        self.section1._compute_dynamic_content()
        self.assertEqual(self.section1.dynamic_content, "<p>Some White content</p>")

    def test_header(self):
        header = self.section1._get_header_object()
        # a header with a child and a grandchild
        self.assertTrue(header.child)
        self.assertTrue(header.child.child)
        self.assertFalse(header.value)
        header.next  # pylint: disable=pointless-statement
        header.child.next  # pylint: disable=pointless-statement
        header.child.child.next  # pylint: disable=pointless-statement
        self.assertEqual(header.value, 1)
        self.assertEqual(header.child.value, 1)
        self.assertEqual(header.child.child.value, 1)
        header.next  # pylint: disable=pointless-statement
        self.assertEqual(header.value, 2)
        header.previous  # pylint: disable=pointless-statement
        self.assertEqual(header.value, 1)
        self.assertEqual(header.child.value, 0)
        self.assertEqual(header.child.child.value, 0)
        header.child.next  # pylint: disable=pointless-statement
        self.assertEqual(header.child.value, 1)
        self.assertEqual(header.child.child.value, 0)
        header.child.child.next  # pylint: disable=pointless-statement
        self.assertEqual(header.child.child.value, 1)
        header.reset  # pylint: disable=pointless-statement
        self.assertFalse(header.value + header.child.value + header.child.child.value)
