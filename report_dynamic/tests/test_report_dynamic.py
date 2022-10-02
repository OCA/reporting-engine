# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestWizardReportDynamic(common.TransactionCase):
    def setUp(self):
        super(TestWizardReportDynamic, self).setUp()
        self.demopartner = self.env.ref("base.user_demo").partner_id
        rd_obj = self.env["report.dynamic"]
        self.rd_template = rd_obj.create(
            {
                "name": "Template for report",
                "model_id": self.env.ref("base.model_res_partner").id,
                "resource_ref": self.env.ref("base.res_partner_1"),
                "is_template": True,
            }
        )
        self.rd_report = rd_obj.create(
            {"name": "Demo report", "template_id": self.rd_template.id}
        )
        self.rd_template2 = rd_obj.create(
            {
                "name": "Template without_children",
                "model_id": self.env.ref("base.model_res_partner").id,
                "resource_ref": self.env.ref("base.res_partner_2"),
                "is_template": True,
            }
        )

    def test_write_resource_ref(self):
        """ Test inverse write on resource_ref """
        res_partner_model = self.env.ref("base.model_res_partner")
        self.rd_report.write(
            {
                "resource_ref": "{},{}".format(
                    res_partner_model.model, self.demopartner.id
                )
            }
        )
        self.assertEquals(self.rd_report.res_id, self.rd_report.resource_ref.id)
        self.assertEquals(self.rd_report.model_id, res_partner_model)

    def test_create_invalid_model(self):
        """ Test that you can't create reports for empty models """
        bli_model = self.env.ref("base.model_base_language_install")
        bli_recs = self.env[bli_model.model].search([])
        if bli_recs:
            bli_recs.unlink()
        with self.assertRaises(ValidationError):
            self.env["report.dynamic"].create(
                {
                    "name": "language template",
                    "model_id": bli_model.id,
                    "is_template": True,
                }
            )

    def test_forbid_template_change(self):
        """ Test that you can't switch a template with reports connected to it """
        with self.assertRaises(ValidationError):
            self.rd_template.write({"is_template": False})

    def test_forbid_model_change(self):
        """ Test that you can't change a template's model with reports connected to it """
        with self.assertRaises(ValidationError):
            self.rd_template.write(
                {
                    "model_id": self.env["ir.model"].search(
                        [("id", "!=", self.rd_template.model_id.id)], limit=1
                    )
                }
            )

    def test_change_template(self):
        """ Test recompute of resource_ref after template change """
        self.assertEqual(self.rd_report.resource_ref, self.rd_template.resource_ref)
        self.rd_report.write({"template_id": self.rd_template2.id})
        self.assertEqual(self.rd_report.resource_ref, self.rd_template2.resource_ref)

    def test_window_action(self):
        """ Tests things related to window actions """
        #  Action should not exist.
        self.assertFalse(self.rd_report.window_action_exists)
        self.rd_report.create_action()
        self.rd_report._compute_window_action_exists()
        self.assertTrue(self.rd_report.window_action_exists)
        # Call create_action again, and see that nothing really happens
        self.rd_report.create_action()
        self.assertEqual(len(self.rd_template.get_window_actions()), 1)
        # unlink action
        self.rd_template.unlink_action()
        self.assertFalse(self.rd_report.window_action_exists)
        self.rd_template.create_action()
        # unlink the reports and see that window action is there
        self.rd_report.unlink()
        self.assertTrue(self.rd_template.window_action_exists)
        # unlink the template and see that the action is gone
        this_model = self.rd_template.model_id
        self.rd_template.unlink()
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
        wiz = wiz_model.create({"template_id": self.rd_template.id})
        ctx = {
            "active_model": "res.partner",
            "active_ids": [self.demopartner.id],
        }
        action = wiz.with_context(ctx).action_generate_reports()
        report_id = action.get("domain")[0][2]
        report = self.env["report.dynamic"].browse(report_id)

        self.assertEquals(len(report), 1)
        self.assertEquals(report.res_id, self.demopartner.id)
        self.assertEquals(report.template_id, self.rd_template)

        # unlocked
        self.assertEquals(report.lock_date, False)
        # lock
        wiz_lock = self.env["wizard.lock.report"].create({"report_id": report.id})
        wiz_lock.action_lock_report()
        self.assertEquals(report.lock_date, fields.Date.today())

    def test_default_wrapper(self):
        self.rd_template.wrapper_report_id = False
        self.assertEqual(self.rd_template.get_template_xml_id(), "web.external_layout")
