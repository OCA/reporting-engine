# Copyright 2009-2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase


class TestReportXlsxHelper(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestReportXlsxHelper, cls).setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        today = date.today()
        p1 = cls.env.ref("base.res_partner_1")
        p2 = cls.env.ref("base.res_partner_2")
        p1.date = today
        p2.date = today
        cls.partners = p1 + p2
        ctx = {
            "report_name": "report_xlsx_helper.test_partner_xlsx",
            "active_model": "res.partner",
            "active_ids": cls.partners.ids,
        }
        cls.report = cls.env["ir.actions.report"].with_context(**ctx)

    def test_report_xlsx_helper(self):
        report_xls = self.report._render_xlsx(None, None)
        self.assertEqual(report_xls[1], "xlsx")
