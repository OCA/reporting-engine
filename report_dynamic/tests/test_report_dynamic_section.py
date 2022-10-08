# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests import common


class TestWizardReportDynamicSection(common.TransactionCase):
    def setUp(self):
        super(TestWizardReportDynamicSection, self).setUp()
        self.rd_obj = self.env["report.dynamic"]
        self.partner_wood_corner = self.env.ref("base.res_partner_1")
        self.partner_deco_addict = self.env.ref("base.res_partner_2")
        self.rd_template = self.rd_obj.create(
            {
                "name": "Template for report",
                "model_id": self.env.ref("base.model_res_partner").id,
                "is_template": True,
            }
        )
        self.tpl_section = self.env["report.dynamic.section"].create(
            {
                "report_id": self.rd_template.id,
                "content": "<p>Some Green content</p>",
                "condition_python": "object.name.startswith('D')",
            }
        )
        self.rd_report = self.rd_obj.new()
        self.rd_report.template_id = self.rd_template.id
        self.rd_report._onchange_template_id()
        self.assertEquals(self.rd_report.model_id.model, "res.partner")
        self.rd_report.res_id = self.partner_wood_corner.id
        self.assertTrue(self.rd_report.resource_ref)
        self.rd_report._onchange_template_id()
        self.report_section = self.rd_report.section_ids
        self.assertEquals(len(self.report_section), 1)
        self.assertIn("D", self.report_section.condition_python)
        self.alias = self.env["report.dynamic.alias"].create(
            {"expression_from": "Green", "expression_to": "Blue"}
        )

    def test_action_view_sections(self):
        action = self.rd_template.action_view_sections()
        self.assertTrue(self.rd_template.section_ids)
        self.assertEquals(action["domain"][0][2], self.rd_template.section_ids.ids)

    def test_section_count(self):
        self.assertEquals(self.rd_template.section_count, 1)
        self.env["report.dynamic.section"].create({"report_id": self.rd_template.id})
        self.assertEqual(self.rd_template.section_count, 2)

    def test_condition_python_preview(self):
        # Initial selected partner record is 'Wood Corner'
        section = self.report_section
        self.assertEquals(section.resource_ref, self.partner_wood_corner)
        # Which does not start with 'D'
        self.assertFalse(section.condition_python_preview)
        self.assertFalse(section.dynamic_content)
        # But now simulate more favourable conditions
        section.condition_python = 'object.name.startswith("W")'
        section._compute_condition_python_preview()
        self.assertTrue(section.condition_python_preview)
        self.assertTrue(section.resource_ref)
        section._compute_dynamic_content()
        self.assertTrue(section.dynamic_content)
        # Check for syntax errors
        section.condition_python = 'object_name.startswith("D")'
        section._compute_condition_python_preview()
        # read preview
        self.assertEqual(
            section.condition_python_preview,
            "<class 'NameError'>: "
            "\"name 'object_name' is not defined"
            '" while evaluating\n\'object_name.startswith("D")\'',
        )
        # nullify condition python
        # an empty python_condition evaluates to string True
        section.condition_python = False
        section._compute_condition_python_preview()
        self.assertEqual(section.condition_python_preview, "True")
        # Finally, check that preview gets False if there's no record
        section.resource_ref = False
        section._compute_condition_python_preview()
        self.assertFalse(section.condition_python_preview)

    def test_compute_dynamic_content(self):
        section = self.report_section
        self.assertFalse(section.dynamic_content)
        section.condition_python = 'object.name.startswith("W")'
        self.alias.active = False
        self.assertIn("Green", section.content)
        self.alias.active = True
        section._compute_dynamic_content()
        self.assertIn("Blue", section.dynamic_content)

    def test_header(self):
        header = self.report_section._get_header_object()
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
        header.reset()
        self.assertFalse(header.value + header.child.value + header.child.child.value)
