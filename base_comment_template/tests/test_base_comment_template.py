# Copyright 2020 NextERP Romania SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common

from .fake_models import ResUsers, setup_test_model, teardown_test_model


class TestCommentTemplate(common.SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup_test_model(cls.env, ResUsers)
        cls.user_obj = cls.env["ir.model"].search([("model", "=", "res.users")])

        cls.user = cls.env.ref("base.user_demo")
        cls.user2 = cls.env.ref("base.demo_user0")
        cls.partner_id = cls.env.ref("base.res_partner_12")
        cls.partner2_id = cls.env.ref("base.res_partner_10")
        cls.company = cls.env["res.company"].create({"name": "Test Company 1"})
        cls.before_template_id = cls.env["base.comment.template"].create(
            {
                "name": "before_lines",
                "text": "Text before lines",
                "model_ids": [(6, 0, cls.user_obj.ids)],
                "priority": 5,
            }
        )
        cls.after_template_id = cls.env["base.comment.template"].create(
            {
                "name": "after_lines",
                "position": "after_lines",
                "text": "Text after lines",
                "model_ids": [(6, 0, cls.user_obj.ids)],
                "priority": 6,
            }
        )

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, ResUsers)
        super(TestCommentTemplate, cls).tearDownClass()

    def test_general_template(self):
        # Check getting default comment template
        templ = self.user.get_comment_template("before_lines")
        self.assertEqual(templ, "Text before lines")
        templ = self.user.get_comment_template("after_lines")
        self.assertEqual(templ, "Text after lines")

    def test_company_general_template(self):
        # Check getting default comment template company
        self.before_template_id.company_id = self.company
        templ = self.user.get_comment_template("before_lines")
        self.assertEqual(templ, "")
        templ = self.user.get_comment_template(
            "before_lines", company_id=self.company.id
        )
        self.assertEqual(templ, "Text before lines")
        templ = self.user.get_comment_template("after_lines")
        self.assertEqual(templ, "Text after lines")

    def test_partner_template(self):
        # Check getting the comment template if partner is set
        self.before_template_id.partner_ids = self.partner2_id.ids
        templ = self.user.get_comment_template(
            "before_lines", partner_id=self.partner2_id.id
        )
        self.assertEqual(templ, "Text before lines")
        templ = self.user.get_comment_template(
            "before_lines", partner_id=self.partner_id.id
        )
        self.assertEqual(templ, "")
        templ = self.user.get_comment_template("after_lines")
        self.assertEqual(templ, "Text after lines")

    def test_partner_template_domain(self):
        # Check getting the comment template if domain is set
        self.before_template_id.partner_ids = self.partner2_id.ids
        self.before_template_id.domain = "[('id', 'in', %s)]" % self.user.ids
        templ = self.user.get_comment_template(
            "before_lines", partner_id=self.partner2_id.id
        )
        self.assertEqual(templ, "Text before lines")
        templ = self.user2.get_comment_template(
            "before_lines", partner_id=self.partner_id.id
        )
        self.assertEqual(templ, "")

    def test_company_partner_template_domain(self):
        # Check getting the comment template with company and if domain is set
        self.before_template_id.company_id = self.company
        templ = self.user.get_comment_template("before_lines")
        self.assertEqual(templ, "")
        templ = self.user.get_comment_template(
            "before_lines", company_id=self.company.id
        )
        self.assertEqual(templ, "Text before lines")
        self.before_template_id.partner_ids = self.partner2_id.ids
        self.before_template_id.domain = "[('id', 'in', %s)]" % self.user.ids
        templ = self.user.get_comment_template(
            "before_lines", partner_id=self.partner2_id.id
        )
        self.assertEqual(templ, "")
        self.before_template_id.company_id = self.env.user.company_id
        templ = self.user.get_comment_template(
            "before_lines", partner_id=self.partner2_id.id
        )
        self.assertEqual(templ, "Text before lines")
        templ = self.user2.get_comment_template(
            "before_lines", partner_id=self.partner2_id.id
        )
        self.assertEqual(templ, "")

    def test_priority(self):
        # Check setting default template will change previous record default
        new_template = self.env["base.comment.template"].create(
            {
                "name": "before_lines",
                "text": "Text before lines 1",
                "model_ids": [(6, 0, self.user_obj.ids)],
                "priority": 2,
            }
        )

        self.assertEqual(new_template.text, "Text before lines 1")
