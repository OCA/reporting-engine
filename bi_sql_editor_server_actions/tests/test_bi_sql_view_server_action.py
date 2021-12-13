# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import SingleTransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestBiSqlViewEditorServerAction(SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestBiSqlViewEditorServerAction, cls).setUpClass()
        cls.bi_sql_view = cls.env["bi.sql.view"]
        cls.ir_actions_server = cls.env["ir.actions.server"]
        cls.server_action_ids = cls.ir_actions_server.create(
            {"name": "x_server_action_name", "state": "code"}
        )
        cls.view = cls.bi_sql_view.create(
            {
                "name": "Partners View 3",
                "is_materialized": True,
                "technical_name": "partners_view_3",
                "query": "SELECT name as x_name, street as x_street,"
                "company_id as x_company_id FROM res_partner "
                "ORDER BY name",
                "server_action_ids": [(6, 0, cls.server_action_ids.ids)],
            }
        )

    def test_server_actions_flow(self):
        self.assertTrue(self.view.server_action_ids)
        self.assertFalse(self.view.server_action_ids.model_id)
        self.view.button_validate_sql_expression()
        self.view.button_create_sql_view_and_model()
        self.assertEqual(self.view.server_action_ids.model_id, self.view.model_id)
        self.view.button_set_draft()
        self.assertTrue(self.view.server_action_ids)
        self.assertFalse(self.view.server_action_ids.model_id)
        self.view.unlink()
        server_action = self.ir_actions_server.search(
            [("name", "=", "x_server_action_name")]
        )
        self.assertEqual(len(server_action), 0, "Server action not deleted")
