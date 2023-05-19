# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResPartner(TransactionCase):
    def setUp(self):
        super(TestResPartner, self).setUp()
        self.partner = self.env.ref("base.res_partner_1")

    def test_export(self):
        action = self.partner.export_xls()
        self.assertEqual(action["type"], "ir.actions.report")
        self.assertEqual(action["report_type"], "xlsx")
        self.assertEqual(
            action["report_name"], "report_xlsx_helper_demo.partner_export_xlsx"
        )
        self.assertDictEqual(action["context"], {"report_file": "partner"})
        self.assertDictEqual(action["data"], {"dynamic_report": True})
