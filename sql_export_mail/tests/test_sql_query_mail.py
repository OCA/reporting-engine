# Copyright (C) 2019 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, Command
from odoo.tests.common import TransactionCase


class TestExportSqlQueryMail(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sql_report_demo = cls.env.ref("sql_export.sql_export_partner")
        cls.sql_report_demo.mail_user_ids = [Command.link(SUPERUSER_ID)]

    def test_sql_query_mail(self):
        mail_obj = self.env["mail.mail"]
        mails = mail_obj.search(
            [("model", "=", "sql.export"), ("res_id", "=", self.sql_report_demo.id)]
        )
        self.assertFalse(mails)
        self.sql_report_demo.create_cron()
        self.assertTrue(self.sql_report_demo.cron_ids)
        self.sql_report_demo.cron_ids.method_direct_trigger()
        mails = mail_obj.search(
            [("model", "=", "sql.export"), ("res_id", "=", self.sql_report_demo.id)]
        )
        self.assertTrue(mails)
        self.assertTrue(mails.attachment_ids)
