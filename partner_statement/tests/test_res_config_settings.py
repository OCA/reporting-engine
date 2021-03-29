# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestResConfigSettings(TransactionCase):
    def setUp(self):
        super().setUp()
        self.config = self.env["res.config.settings"]
        self.cr.execute(
            "SELECT uid FROM res_groups_users_rel "
            "WHERE gid IN (SELECT res_id FROM ir_model_data "
            "   WHERE module='account' AND name='group_account_invoice') "
            "ORDER BY uid DESC LIMIT 1"
        )
        self.account_user = self.cr.fetchone()[0]
        self.user_obj = self.env["res.users"].with_user(self.account_user)

    def test_groups(self):
        conf = self.config.create(
            {
                "default_aging_type": "months",
                "group_activity_statement": True,
                "group_outstanding_statement": False,
            }
        )
        conf.set_values()
        self.assertFalse(
            self.user_obj._has_group("partner_statement.group_outstanding_statement")
        )
        self.assertTrue(
            self.user_obj._has_group("partner_statement.group_activity_statement")
        )
        res = self.env["ir.default"].get("activity.statement.wizard", "aging_type")
        self.assertEqual(res, "months")
