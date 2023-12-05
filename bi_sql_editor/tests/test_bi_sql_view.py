# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import SingleTransactionCase


@tagged("-at_install", "post_install")
class TestBiSqlViewEditor(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.bi_sql_view = cls.env["bi.sql.view"]
        cls.group_bi_manager = cls.env.ref(
            "sql_request_abstract.group_sql_request_manager"
        )
        cls.group_bi_no_access = cls.env.ref("base.group_user")
        cls.demo_user = cls.env.ref("base.user_demo")
        cls.view = cls.env.ref("bi_sql_editor.partner_sql_view")

    @classmethod
    def _get_user(cls, access_level=False):
        if access_level == "manager":
            cls.demo_user.write({"groups_id": [(6, 0, cls.group_bi_manager.ids)]})
        else:
            cls.demo_user.write({"groups_id": [(6, 0, cls.group_bi_no_access.ids)]})
        return cls.demo_user

    def test_process_view(self):
        copy_view = self.view.copy(default={"technical_name": "test_process_view"})
        self.assertEqual(copy_view.state, "draft")
        copy_view.button_validate_sql_expression()
        self.assertEqual(copy_view.state, "sql_valid")

        field_lines = copy_view.bi_sql_view_field_ids
        self.assertEqual(len(field_lines), 3)
        field_lines.filtered(lambda x: x.name == "x_company_id").is_index = True

        copy_view.button_create_sql_view_and_model()
        self.assertEqual(copy_view.state, "model_valid")

        field_lines.filtered(lambda x: x.name == "x_name").tree_visibility = "invisible"
        field_lines.filtered(
            lambda x: x.name == "x_street"
        ).tree_visibility = "optional_hide"
        field_lines.filtered(
            lambda x: x.name == "x_company_id"
        ).tree_visibility = "optional_show"

        field_lines.filtered(lambda x: x.name == "x_company_id").is_group_by = True

        field_lines.filtered(lambda x: x.name == "x_company_id").graph_type = "row"

        copy_view.button_create_ui()
        self.assertEqual(copy_view.state, "ui_valid")
        copy_view.button_update_model_access()
        self.assertEqual(copy_view.has_group_changed, False)
        # Check that cron works correctly
        copy_view.cron_id.method_direct_trigger()

    def test_copy(self):
        copy_view = self.view.copy(default={"technical_name": "test_copy"})
        self.assertEqual(copy_view.name, f"{self.view.name} (Copy)")

    def test_security(self):
        with self.assertRaises(AccessError):
            self.bi_sql_view.with_user(self._get_user()).search(
                [("name", "=", self.view.name)]
            )
        bi = self.bi_sql_view.with_user(self._get_user("manager")).search(
            [("name", "=", self.view.name)]
        )
        self.assertEqual(
            len(bi), 1, "Bi Manager should have access to bi %s" % self.view.name
        )

    def test_unlink(self):
        copy_view = self.view.copy(
            default={
                "name": "Test Unlink",
                "technical_name": "test_unlink",
            }
        )
        view_name = copy_view.name
        copy_view.button_validate_sql_expression()
        copy_view.button_create_sql_view_and_model()
        copy_view.button_create_ui()
        self.assertEqual(copy_view.state, "ui_valid")
        with self.assertRaises(UserError):
            copy_view.unlink()
        copy_view.button_set_draft()
        self.assertNotEqual(
            copy_view.cron_id,
            False,
            "Set to draft materialized view should not unlink cron",
        )
        copy_view.unlink()
        res = self.bi_sql_view.search([("name", "=", view_name)])
        self.assertEqual(len(res), 0, "View not deleted")

    def test_many2one_not_found(self):
        copy_view = self.view.copy(
            default={"technical_name": "test_many2one_not_found"}
        )

        copy_view.query = "SELECT parent_id as x_weird_name_id FROM res_partner;"
        copy_view.button_validate_sql_expression()
        field_lines = copy_view.bi_sql_view_field_ids
        self.assertEqual(len(field_lines), 1)
        self.assertEqual(field_lines[0].ttype, "many2one")
        self.assertEqual(field_lines[0].many2one_model_id.id, False)

        with self.assertRaises(ValidationError):
            copy_view.button_create_sql_view_and_model()
