# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestReportLabel(common.TransactionCase):
    def setUp(self):
        super().setUp()
        paperformat = self.env["report.paperformat"].create(
            {"name": "Test label paperformat", "format": "A4"}
        )
        label_paperformat = self.env["report.paperformat.label"].create(
            {
                "name": "Test partner labels",
                "paperformat_id": paperformat.id,
                "label_width": 70,
                "label_height": 49.5,
            }
        )
        template = self.env["ir.ui.view"].create(
            {
                "name": "Test partner label template",
                "type": "qweb",
                "key": "report_label.test_label_template",
                "arch": "<address t-field='record.self'/>",
            }
        )
        self.partner_label = self.env["ir.actions.server"].create(
            {
                "name": "Print Test Address Labels",
                "state": "report_label",
                "model_id": self.env.ref("base.model_res_partner").id,
                "label_paperformat_id": label_paperformat.id,
                "label_template_view_id": template.id,
            }
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
