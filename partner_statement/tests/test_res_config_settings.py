# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestResConfigSettings(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        cls.config = cls.env["res.config.settings"]
        cls.cr.execute(
            "SELECT uid FROM res_groups_users_rel "
            "WHERE gid IN (SELECT res_id FROM ir_model_data "
            "   WHERE module='account' AND name='group_account_invoice') "
            "ORDER BY uid DESC LIMIT 1"
        )
        cls.account_user = cls.cr.fetchone()[0]
        cls.user_obj = cls.env["res.users"].with_user(cls.account_user)

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
        res = (
            self.env["activity.statement.wizard"]
            .with_context(active_ids=[1])
            .create({})
        )
        self.assertEqual(res.aging_type, "months")
