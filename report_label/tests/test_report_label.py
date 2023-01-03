# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestReportLabel(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_label = self.env.ref(
            "report_label.actions_server_label_partner_address"
        )

    def test_01_print_partner_label(self):
        self.partner_label.create_action()
        action = self.partner_label.run()
        model = action["res_model"]
        context = action["context"]
        context.update(
            {
                "active_model": "res.partner",
                "active_ids": self.env["res.partner"].search([]).ids,
                "discard_logo_check": True,
            }
        )
        wizard = self.env[model].with_context(**context).create({})
        report_action = wizard.print_report()
        self.assertEqual(report_action["type"], "ir.actions.report")
