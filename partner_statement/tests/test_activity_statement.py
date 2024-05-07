# Copyright 2018 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from freezegun import freeze_time

from odoo import fields
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestActivityStatement(TransactionCase):
    """Tests for Activity Statement."""

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
        cls.res_users_model = cls.env["res.users"]
        cls.company = cls.env.ref("base.main_company")
        cls.company.external_report_layout_id = cls.env.ref(
            "web.external_layout_standard"
        )
        cls.partner1 = cls.env.ref("base.res_partner_1")
        cls.partner2 = cls.env.ref("base.res_partner_2")
        cls.user = new_test_user(
            cls.env, login="user_1", groups="account.group_account_user"
        )
        cls.statement_model = cls.env["report.partner_statement.activity_statement"]
        cls.wiz = cls.env["activity.statement.wizard"]
        cls.report_name = "partner_statement.activity_statement"
        cls.report_name_xlsx = "p_s.report_activity_statement_xlsx"
        cls.report_title = "Activity Statement"
        cls.today = fields.Date.context_today(cls.wiz)

    def test_customer_activity_statement(self):

        wiz_id = self.wiz.with_context(
            active_ids=[self.partner1.id, self.partner2.id]
        ).create({})

        wiz_id.aging_type = "months"
        wiz_id.show_aging_buckets = False

        statement = wiz_id.button_export_pdf()

        self.assertDictEqual(
            statement,
            {
                **{
                    "type": "ir.actions.report",
                    "report_name": self.report_name,
                    "report_type": "qweb-pdf",
                },
                **statement,
            },
            "There was an error and the PDF report was not generated.",
        )

        statement_xlsx = wiz_id.button_export_xlsx()

        self.assertDictEqual(
            statement_xlsx,
            {
                **{
                    "type": "ir.actions.report",
                    "report_name": self.report_name_xlsx,
                    "report_type": "xlsx",
                },
                **statement_xlsx,
            },
            "There was an error and the PDF report was not generated.",
        )

        data = wiz_id._prepare_statement()
        docids = data["partner_ids"]
        report = self.statement_model._get_report_values(docids, data)
        self.assertIsInstance(
            report, dict, "There was an error while compiling the report."
        )
        self.assertIn(
            "bucket_labels", report, "There was an error while compiling the report."
        )

    def test_customer_activity_report_no_wizard(self):
        docids = [self.partner1.id, self.partner2.id]
        report = self.statement_model._get_report_values(docids, False)
        self.assertIsInstance(
            report, dict, "There was an error while compiling the report."
        )
        self.assertIn(
            "bucket_labels", report, "There was an error while compiling the report."
        )

    def test_date_formatting(self):
        date_fmt = "%d/%m/%Y"
        test_date = date(2018, 9, 30)
        res = self.statement_model._format_date_to_partner_lang(test_date, date_fmt)
        self.assertEqual(res, "30/09/2018")

        test_date_string = "2018-09-30"
        res = self.statement_model._format_date_to_partner_lang(
            test_date_string, date_fmt
        )
        self.assertEqual(res, "30/09/2018")

    @freeze_time("2024-05-01")
    def test_onchange_aging_type(self):
        """Test that partner data is filled accordingly"""
        self.today = fields.Date.context_today(self.wiz)
        wiz_id = self.wiz.with_context(
            active_ids=[self.partner1.id, self.partner2.id]
        ).new()
        wiz_id.aging_type = "months"
        wiz_id.onchange_aging_type()
        self.assertEqual(wiz_id.date_end.month, wiz_id.date_start.month)
        self.assertTrue(wiz_id.date_end.day > wiz_id.date_start.day)
        self.assertTrue(wiz_id.date_end < self.today)

        wiz_id.aging_type = "days"
        wiz_id.onchange_aging_type()
        self.assertEqual((wiz_id.date_end - wiz_id.date_start).days, 30)
        self.assertTrue(wiz_id.date_end == self.today)

    @freeze_time("2024-05-31")
    def test_onchange_aging_type2(self):
        """Test that partner data is filled accordingly"""
        self.today = fields.Date.context_today(self.wiz)
        wiz_id = self.wiz.with_context(
            active_ids=[self.partner1.id, self.partner2.id]
        ).new()
        wiz_id.aging_type = "months"
        wiz_id.onchange_aging_type()
        self.assertEqual(wiz_id.date_end.month, wiz_id.date_start.month)
        self.assertTrue(wiz_id.date_end.day > wiz_id.date_start.day)
        self.assertTrue(wiz_id.date_end < self.today)

        wiz_id.aging_type = "days"
        wiz_id.onchange_aging_type()
        self.assertEqual((wiz_id.date_end - wiz_id.date_start).days, 31)
        self.assertTrue(wiz_id.date_end == self.today)
