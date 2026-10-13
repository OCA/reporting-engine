# Copyright 2009-2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestReportXlsxHelper(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partners = cls.env["res.partner"].create(
            [
                {"name": "Test Partner 1"},
                {"name": "Test Partner 2"},
            ]
        )

    def test_report_xlsx_helper(self):
        ctx = {
            "report_name": "report_xlsx_helper.test_partner_xlsx",
            "active_model": "res.partner",
            "active_ids": self.partners.ids,
        }
        report = self.env["ir.actions.report"].with_context(**ctx)
        report_xls = report._render_xlsx(None, None, None)
        self.assertEqual(report_xls[1], "xlsx")
