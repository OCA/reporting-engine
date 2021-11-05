# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tests.common import SingleTransactionCase


@tagged("-at_install", "post_install")
class TestBiSqlViewEditor(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestBiSqlViewEditor, cls).setUpClass()

        cls.res_partner = cls.env["res.partner"]
        cls.res_users = cls.env["res.users"]
        cls.bi_sql_view = cls.env["bi.sql.view"]
        cls.group_bi_user = cls.env.ref(
            "sql_request_abstract.group_sql_request_manager"
        )
        cls.group_user = cls.env.ref("base.group_user")
        cls.view = cls.bi_sql_view.create(
            {
                "name": "Partners View 2",
                "is_materialized": True,
                "technical_name": "partners_view_2",
                "query": "SELECT name as x_name, street as x_street,"
                "company_id as x_company_id FROM res_partner "
                "ORDER BY name",
            }
        )
        cls.company = cls.env.ref("base.main_company")
        # Create bi user
        cls.bi_user = cls._create_user("bi_user", cls.group_bi_user, cls.company)
        cls.no_bi_user = cls._create_user("no_bi_user", cls.group_user, cls.company)

    @classmethod
    def _create_user(cls, login, groups, company):
        """Create a user."""
        user = cls.res_users.create(
            {
                "name": login,
                "login": login,
                "password": "demo",
                "email": "example@yourcompany.com",
                "company_id": company.id,
                "groups_id": [(6, 0, groups.ids)],
            }
        )
        return user

    def test_process_view(self):
        view = self.view
        self.assertEqual(view.state, "draft", "state not draft")
        view.button_validate_sql_expression()
        self.assertEqual(view.state, "sql_valid", "state not sql_valid")
        view.button_create_sql_view_and_model()
        self.assertEqual(view.state, "model_valid", "state not model_valid")
        view.button_create_ui()
        self.assertEqual(view.state, "ui_valid", "state not ui_valid")
        view.button_update_model_access()
        self.assertEqual(view.has_group_changed, False, "has_group_changed not False")
        cron_res = view.cron_id.method_direct_trigger()
        self.assertEqual(cron_res, True, "something went wrong with the cron")

    def test_copy(self):
        copy_view = self.view.copy()
        self.assertEqual(copy_view.name, "Partners View 2 (Copy)", "Wrong name")

    def test_security(self):
        with self.assertRaises(AccessError):
            self.bi_sql_view.with_user(self.no_bi_user.id).search(
                [("name", "=", "Partners View 2")]
            )
        bi = self.bi_sql_view.with_user(self.bi_user.id).search(
            [("name", "=", "Partners View 2")]
        )
        self.assertEqual(
            len(bi), 1, "Bi user should not have access to " "bi %s" % self.view.name
        )

    def test_unlink(self):
        self.assertEqual(self.view.state, "ui_valid", "state not ui_valid")
        with self.assertRaises(UserError):
            self.view.unlink()
        self.view.button_set_draft()
        self.assertNotEqual(
            self.view.cron_id,
            False,
            "Set to draft materialized view should" " not unlink cron",
        )
        self.view.unlink()
        res = self.bi_sql_view.search([("name", "=", "Partners View 2")])
        self.assertEqual(len(res), 0, "View not deleted")
