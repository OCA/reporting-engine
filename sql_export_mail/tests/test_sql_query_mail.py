# Copyright (C) 2019 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestExportSqlQueryMail(TransactionCase):
    def setUp(self):
        super(TestExportSqlQueryMail, self).setUp()
        self.sql_report_demo = self.env.ref("sql_export.sql_export_partner")
        self.sql_report_demo.write({"mail_user_ids": [(4, SUPERUSER_ID)]})

    def test_sql_query_mail(self):
        """Check the general execution"""
        self.check_before_change()
        self.check_execution()

    def test_not_able_add_user(self):
        """if there are field_ids, mail_user_ids can not be set"""
        sql_report_demo_with_partner = self.env.ref(
            "sql_export.sql_export_partner_with_variables"
        )
        with self.assertRaises(UserError):
            sql_report_demo_with_partner.write(
                {"mail_user_ids": [(4, self.env.ref("base.user_demo").id)]}
            )

    def test_sql_query_mail_company(self):
        """Check the general execution with %(company_id)s"""
        self.check_before_change()
        self.sql_report_demo.write(
            {
                "mail_user_ids": [(4, self.env.ref("base.user_demo").id)],
                "query": """SELECT name, street
                                    FROM res_partner where company_id = %(company_id)s""",
            }
        )
        self.check_execution()

    def test_sql_query_mail_company_user(self):
        """Check the general execution with %(company_id)s and %(user_id)s)"""
        self.check_before_change()
        self.sql_report_demo.write(
            {
                "mail_user_ids": [(4, self.env.ref("base.user_demo").id)],
                "query": """SELECT name, street FROM res_partner
                                    where company_id = %(company_id)s and id in (
                                    select partner_id from res_users where id = %(user_id)s)""",
            }
        )
        self.check_execution()

    def check_before_change(self):
        """Check if there are no mails before changing the sql report"""
        mails = self.env["mail.mail"].search(
            [("model", "=", "sql.export"), ("res_id", "=", self.sql_report_demo.id)]
        )
        self.assertFalse(mails)

    def check_execution(self):
        """Check if the cron could be created and the mail sending is working"""
        self.sql_report_demo.create_cron()
        self.assertTrue(self.sql_report_demo.cron_ids)
        self.sql_report_demo.cron_ids.method_direct_trigger()
        mails = self.env["mail.mail"].search(
            [("model", "=", "sql.export"), ("res_id", "=", self.sql_report_demo.id)]
        )
        self.assertTrue(mails)
        self.assertTrue(mails.attachment_ids)
