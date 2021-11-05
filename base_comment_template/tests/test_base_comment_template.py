# Copyright 2020 NextERP Romania SRL
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common

from .fake_models import ResUsers, setup_test_model, teardown_test_model


class TestCommentTemplate(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup_test_model(cls.env, ResUsers)
        cls.user_obj = cls.env.ref("base.model_res_users")
        cls.user = cls.env.ref("base.user_demo")
        cls.user2 = cls.env.ref("base.demo_user0")
        cls.partner_id = cls.env.ref("base.res_partner_12")
        cls.partner2_id = cls.env.ref("base.res_partner_10")
        cls.main_company = cls.env.ref("base.main_company")
        cls.company = cls.env["res.company"].create({"name": "Test company"})
        cls.before_template_id = cls.env["base.comment.template"].create(
            {
                "name": "Top template",
                "text": "Text before lines",
                "model_ids": [(6, 0, cls.user_obj.ids)],
                "company_id": cls.company.id,
            }
        )
        cls.after_template_id = cls.env["base.comment.template"].create(
            {
                "name": "Bottom template",
                "position": "after_lines",
                "text": "Text after lines",
                "model_ids": [(6, 0, cls.user_obj.ids)],
                "company_id": cls.company.id,
            }
        )
        cls.user.partner_id.base_comment_template_ids = [
            (4, cls.before_template_id.id),
            (4, cls.after_template_id.id),
        ]

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, ResUsers)
        super(TestCommentTemplate, cls).tearDownClass()

    def test_template_name_get(self):
        self.assertEqual(
            self.before_template_id.display_name,
            "Top template (Top)",
        )
        self.assertEqual(
            self.after_template_id.display_name,
            "Bottom template (Bottom)",
        )

    def test_general_template(self):
        # Need to force _compute because only trigger when partner_id have changed
        self.user._compute_comment_template_ids()
        # Check getting default comment template
        self.assertTrue(self.before_template_id in self.user.comment_template_ids)
        self.assertTrue(self.after_template_id in self.user.comment_template_ids)

    def test_partner_template(self):
        self.partner2_id.base_comment_template_ids = [
            (4, self.before_template_id.id),
            (4, self.after_template_id.id),
        ]
        self.assertTrue(
            self.before_template_id in self.partner2_id.base_comment_template_ids
        )
        self.assertTrue(
            self.after_template_id in self.partner2_id.base_comment_template_ids
        )

    def test_partner_template_domain(self):
        # Check getting the comment template if domain is set
        self.partner2_id.base_comment_template_ids = [
            (4, self.before_template_id.id),
            (4, self.after_template_id.id),
        ]
        self.before_template_id.domain = "[('id', 'in', %s)]" % self.user.ids
        self.assertTrue(
            self.before_template_id in self.partner2_id.base_comment_template_ids
        )
        self.assertTrue(
            self.before_template_id not in self.partner_id.base_comment_template_ids
        )
