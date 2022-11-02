# Copyright 2020 NextERP Romania SRL
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tools.misc import mute_logger

from .fake_models import ResUsers, setup_test_model, teardown_test_model


class TestCommentTemplate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        setup_test_model(cls.env, ResUsers)
        cls.user_obj = cls.env.ref("base.model_res_users")
        cls.user = cls.env.ref("base.user_demo")
        cls.user2 = cls.env.ref("base.demo_user0")
        cls.partner_id = cls.env.ref("base.res_partner_12")
        cls.partner2_id = cls.env.ref("base.res_partner_10")
        cls.ResPartnerTitle = cls.env["res.partner.title"]
        cls.main_company = cls.env.ref("base.main_company")
        cls.company = cls.env["res.company"].create({"name": "Test company"})
        cls.before_template_id = cls.env["base.comment.template"].create(
            {
                "name": "Top template",
                "text": "Text before lines",
                "models": cls.user_obj.model,
                "company_id": cls.company.id,
            }
        )
        cls.after_template_id = cls.env["base.comment.template"].create(
            {
                "name": "Bottom template",
                "position": "after_lines",
                "text": "Text after lines",
                "models": cls.user_obj.model,
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
        return super(TestCommentTemplate, cls).tearDownClass()

    def test_template_model_ids(self):
        self.assertIn(
            self.user_obj.model, self.before_template_id.mapped("model_ids.model")
        )
        self.assertEqual(len(self.before_template_id.model_ids), 1)
        self.assertIn(
            self.user_obj.model, self.after_template_id.mapped("model_ids.model")
        )
        self.assertEqual(len(self.after_template_id.model_ids), 1)

    def test_template_models_constrains(self):
        with self.assertRaises(ValidationError):
            self.env["base.comment.template"].create(
                {
                    "name": "Custom template",
                    "text": "Text",
                    "models": "incorrect.model",
                    "company_id": self.company.id,
                }
            )

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

    def test_render_comment_text(self):
        expected_text = "Test comment render %s" % self.user.name
        self.before_template_id.text = "Test comment render {{object.name}}"
        with self.with_user(self.user.login):
            self.assertEqual(
                self.user.render_comment(self.before_template_id), expected_text
            )

    def test_render_comment_text_(self):
        with mute_logger("odoo.addons.base.models.ir_translation"):
            self.env["base.language.install"].create(
                {"lang": "ro_RO", "overwrite": True}
            ).lang_install()
        with mute_logger("odoo.tools.translate"):
            self.env["base.update.translations"].create({"lang": "ro_RO"}).act_update()
        partner_title = self.ResPartnerTitle.create(
            {"name": "Ambassador", "shortcut": "Amb."}
        )
        # Adding translated terms
        ctx = dict(lang="ro_RO")
        partner_title.with_context(**ctx).write(
            {"name": "Ambasador", "shortcut": "Amb."}
        )
        self.user.partner_id.title = partner_title
        self.before_template_id.text = "Test comment render {{object.title.name}}"

        expected_en_text = "Test comment render Ambassador"
        expected_ro_text = "Test comment render Ambasador"
        with self.with_user(self.user.login):
            self.assertEqual(
                self.user.render_comment(self.before_template_id), expected_en_text
            )
            self.assertEqual(
                self.user.with_context(**ctx).render_comment(self.before_template_id),
                expected_ro_text,
            )

    def test_partner_template_wizaard(self):
        partner_preview = (
            self.env["base.comment.template.preview"]
            .with_context(default_base_comment_template_id=self.before_template_id.id)
            .create({})
        )
        self.assertTrue(partner_preview)
        default = (
            self.env["base.comment.template.preview"]
            .with_context(default_base_comment_template_id=self.before_template_id.id)
            .default_get(partner_preview._fields)
        )
        self.assertTrue(default.get("base_comment_template_id"))
        resource_ref = partner_preview._selection_target_model()
        self.assertTrue(len(resource_ref) >= 2)
        partner_preview._compute_no_record()
        self.assertTrue(partner_preview.no_record)

    def test_partner_commercial_fields(self):
        self.assertTrue(
            "base_comment_template_ids" in self.env["res.partner"]._commercial_fields()
        )
