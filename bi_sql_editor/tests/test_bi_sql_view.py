# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError, UserError
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
        self.assertEqual(self.view.state, "draft")
        self.view.button_validate_sql_expression()
        self.assertEqual(self.view.state, "sql_valid")
        self.view.button_create_sql_view_and_model()
        self.assertEqual(self.view.state, "model_valid")
        self.view.button_create_ui()
        self.assertEqual(self.view.state, "ui_valid")
        self.view.button_update_model_access()
        self.assertEqual(self.view.has_group_changed, False)
        # Check that cron works correctly
        self.view.cron_id.method_direct_trigger()

    def test_copy(self):
        copy_view = self.view.copy()
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
        view_name = self.view.name
        self.assertEqual(self.view.state, "ui_valid")
        with self.assertRaises(UserError):
            self.view.unlink()
        self.view.button_set_draft()
        self.assertNotEqual(
            self.view.cron_id,
            False,
            "Set to draft materialized view should not unlink cron",
        )
        self.view.unlink()
        res = self.bi_sql_view.search([("name", "=", view_name)])
        self.assertEqual(len(res), 0, "View not deleted")
