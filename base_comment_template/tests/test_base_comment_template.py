# Copyright 2020 NextERP Romania SRL
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.orm.model_classes import add_to_registry
from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestCommentTemplate(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        from .fake_models import TestResUsers

        add_to_registry(cls.registry, TestResUsers)
        cls.registry._setup_models__(cls.env.cr, ["test.res.users"])
        cls.registry.init_models(
            cls.env.cr,
            ["test.res.users"],
            {"models_to_check": True},
        )
        cls.addClassCleanup(cls.registry.__delitem__, "test.res.users")

        cls.test_user_obj = cls.env["ir.model"].search(
            [("model", "=", "test.res.users")], limit=1
        )
        cls.user = cls.env["test.res.users"].create(
            {
                "name": "Test User",
                "login": "test_user",
                "email": "test_user@example.com",
            }
        )
        cls.user2 = cls.env["test.res.users"].create(
            {
                "name": "Test User 2",
                "login": "test_user_2",
                "email": "test_user_2@example.com",
            }
        )
        cls.partner_id = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.partner2_id = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.ResPartnerCategory = cls.env["res.partner.category"]
        cls.main_company = cls.env.ref("base.main_company")
        cls.company = cls.env["res.company"].create({"name": "Test company"})
        cls.before_template_id = cls.env["base.comment.template"].create(
            {
                "name": "Top template",
                "text": "Text before lines",
                "models": cls.test_user_obj.model,
                "company_id": cls.company.id,
            }
        )
        cls.after_template_id = cls.env["base.comment.template"].create(
            {
                "name": "Bottom template",
                "position": "after_lines",
                "text": "Text after lines",
                "models": cls.test_user_obj.model,
                "company_id": cls.company.id,
            }
        )
        cls.user.partner_id.base_comment_template_ids = [
            (4, cls.before_template_id.id),
            (4, cls.after_template_id.id),
        ]

    def test_template_model_ids(self):
        self.assertIn(
            self.test_user_obj.model, self.before_template_id.mapped("model_ids.model")
        )
        self.assertEqual(len(self.before_template_id.model_ids), 1)
        self.assertIn(
            self.test_user_obj.model, self.after_template_id.mapped("model_ids.model")
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

    def test_template_display_name(self):
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

    def test_global_template(self):
        # Need to force _compute because only trigger when partner_id have changed
        global_template = self.env["base.comment.template"].create(
            {
                "name": "Top template",
                "text": "Text before lines",
                "models": self.test_user_obj.model,
                "company_id": self.company.id,
            }
        )
        self.user._compute_comment_template_ids()
        # Check getting default comment template
        self.assertNotIn(global_template, self.user.comment_template_ids)
        global_template.global_template = True
        self.user._compute_comment_template_ids()
        self.assertIn(global_template, self.user.comment_template_ids)

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
        self.before_template_id.domain = f"[('id', 'in', {self.user.ids})]"
        self.assertTrue(
            self.before_template_id in self.partner2_id.base_comment_template_ids
        )
        self.assertTrue(
            self.before_template_id not in self.partner_id.base_comment_template_ids
        )

    def test_render_comment_text(self):
        expected_text = f"Test comment render {self.user.name}"
        self.before_template_id.text = "Test comment render {{object.name}}"
        self.assertEqual(
            self.user.render_comment(self.before_template_id), expected_text
        )

    def test_render_comment_text_(self):
        ro_RO_lang = (
            self.env["res.lang"]
            .with_context(active_test=False)
            .search([("code", "=", "ro_RO")])
        )
        with mute_logger("odoo.addons.base.models.ir_translation"):
            self.env["base.language.install"].create(
                {"overwrite": True, "lang_ids": [(6, 0, [ro_RO_lang.id])]}
            ).lang_install()

        module = self.env.ref("base.module_test_translation_import")
        export = self.env["base.language.export"].create(
            {"lang": "ro_RO", "format": "po", "modules": [Command.set([module.id])]}
        )
        export.act_getfile()
        po_file = export.data
        self.assertIsNotNone(po_file)

        partner_category = self.ResPartnerCategory.create({"name": "Ambassador"})
        # Adding translated terms
        ctx = dict(lang="ro_RO")
        partner_category.with_context(**ctx).write({"name": "Ambasador"})
        self.user.partner_id.category_id = partner_category
        self.before_template_id.text = "Test comment render {{object.category_id.name}}"

        expected_en_text = "Test comment render Ambassador"
        expected_ro_text = "Test comment render Ambasador"
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
