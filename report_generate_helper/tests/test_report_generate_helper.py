from odoo.tests import common


class TestReportLabel(common.TransactionCase):
    def test_get_report(self):
        module = self.env["ir.module.module"].search([])[1]
        self.assertTrue(module.get_report("base.report_irmodulereference"))
