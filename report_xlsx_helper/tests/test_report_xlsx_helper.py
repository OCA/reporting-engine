# Copyright 2009-2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestReportXlsxHelper(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partners = cls.env["res.partner"].create(
            [
                {"name": "Test Partner 1"},
                {"name": "Test Partner 2"},
            ]
        )
        ctx = {
            "report_name": "report_xlsx_helper.test_partner_xlsx",
            "active_model": "res.partner",
            "active_ids": cls.partners.ids,
        }
        cls.report = cls.env["ir.actions.report"].with_context(**ctx)

    def test_report_xlsx_helper(self):
        report_xls = self.report._render_xlsx(None, None, None)
        self.assertEqual(report_xls[1], "xlsx")
