from odoo.tests import common
from ast import literal_eval


class TestReportLabel(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.partner_label = self.env.ref(
            "report_label.actions_server_label_partner_address")

    def test_01_print_partner_label(self):
        self.partner_label.create_action()
        action = self.partner_label.run()
        model = action["res_model"]
        context = literal_eval(action["context"])
        context["active_model"] = "res.partner"
        context["active_ids"] = self.env["res.partner"].search([]).ids
        wizard = self.env[model].with_context(context).create({})
        report_action = wizard.print_report()
        self.assertEquals(report_action["type"], "ir.actions.report")
