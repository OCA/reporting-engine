# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common


class TestWizardReportDynamic(common.TransactionCase):
    def setUp(self):
        super(TestWizardReportDynamic, self).setUp()
        # use the demodata.
        self.RD_template = self.env.ref("report_dynamic.demo_report_2")
        self.RD_report = self.env.ref("report_dynamic.demo_report_1")
        self.demouser = self.env.ref("base.user_demo")

    def test_report_crud_operations(self):
        # test inverse write on resource_ref
        res_partner_model = self.env.ref("base.model_res_partner")
        self.RD_report.write(
            {"resource_ref": "{},{}".format(res_partner_model.model, self.demouser.id)}
        )
        self.assertEquals(self.RD_report.res_id, self.RD_report.resource_ref.id)
        self.assertEquals(self.RD_report.model_id, res_partner_model)
        # Check for models with existing records in db
        new_model = self.env.ref("base.model_base_language_install")
        with self.assertRaises(UserError) as e:
            BLI_template = self.env["report.dynamic"].create(
                {
                    "name": "language template",
                    "resource_ref": self.env["base.language.install"]
                    .search([], limit=1)
                    .id,
                    "model_id": new_model.id,
                    "is_template": True,
                }
            )
            BLI_report = self.env["report.dynamic"].create(
                {"name": "language template", "template_id": BLI_template.id}
            )
            self.env["base.language.install"].search([]).unlink()
            BLI_report._compute_resource_ref()
        self.assertEqual(
            e.exception.name,
            "No sample record exists for Model base.language.install. "
            "Please create one before proceeding",
        )
        # Check that you can't switch a template
        # with reports connected to it
        with self.assertRaises(UserError) as e:
            BLI_template.write({"is_template": False})
        self.assertEqual(
            e.exception.name,
            "You cannot switch this template because it has reports connected to it",
        )
        # Check that you can't change a template's model
        # with reports connected to it
        with self.assertRaises(UserError) as e:
            BLI_template.write(
                {
                    "model_id": self.env["ir.model"].search(
                        [("id", "!=", BLI_template.model_id.id)], limit=1
                    )
                }
            )
        self.assertEqual(
            e.exception.name, "You cannot change model for this report",
        )
        # Check that as soon as we switch template for a report,
        # resource_ref gets recomputed
        self.assertEqual(BLI_report.resource_ref, BLI_template.resource_ref)
        BLI_report.write({"template_id": self.RD_template.id})
        self.assertEqual(BLI_report.resource_ref, self.RD_template.resource_ref)

    def test_window_action(self):
        #  Action should not exist.
        self.assertFalse(self.RD_report.window_action_exists)
        self.RD_report.create_action()
        self.RD_report._compute_window_action_exists()
        self.assertTrue(self.RD_report.window_action_exists)
        # Call create_action again, and see that nothing really happens
        self.RD_report.create_action()
        self.assertEqual(len(self.RD_template.get_window_actions()), 1)
        # unlink action
        self.RD_template.unlink_action()
        self.assertFalse(self.RD_report.window_action_exists)
        self.RD_template.create_action()
        # unlink the reports and see that window action is there
        self.RD_report.unlink()
        self.assertTrue(self.RD_template.window_action_exists)
        # unlink the template and see that the action is gone
        this_model = self.RD_template.model_id
        self.RD_template.unlink()
        self.assertFalse(
            self.env["ir.actions.act_window"].search(
                [
                    ("res_model", "=", "wizard.report.dynamic"),
                    ("binding_model_id", "=", this_model.id),
                ]
            )
        )

    def test_wizards(self):
        wiz_model = self.env["wizard.report.dynamic"]
        # TODO emulate form
        wiz = wiz_model.create({"template_id": self.RD_template.id})
        ctx = {
            "active_model": "res.partner",
            "active_ids": [self.demouser.partner_id.id],
        }
        action = wiz.with_context(ctx).action_generate_reports()
        report_id = action.get("domain")[0][2]
        report = self.env["report.dynamic"].browse(report_id)

        self.assertEquals(len(report), 1)
        self.assertEquals(report.res_id, self.demouser.partner_id.id)
        self.assertEquals(report.template_id, self.RD_template)

        # unlocked
        self.assertEquals(report.lock_date, False)
        # lock
        wiz_lock = self.env["wizard.lock.report"].create({"report_id": report.id})
        wiz_lock.action_lock_report()
        self.assertEquals(report.lock_date, fields.Date.today())

    def test_default_wrapper(self):
        self.RD_template.wrapper_report_id = False
        self.assertEqual(self.RD_template.get_template_xml_id(), "web.external_layout")

    def test_active(self):
        # Test active/archived
        self.assertTrue(self.RD_template.active)
        self.RD_template.action_toggle_active()
        self.assertFalse(self.RD_template.active)
