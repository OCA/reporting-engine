# Copyright 2023 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPartnerExportXLSX(TransactionCase):
    def setUp(self):
        super(TestPartnerExportXLSX, self).setUp()
        self.partner_export_xlsx = self.env[
            "report.report_xlsx_helper_demo.partner_export_xlsx"
        ]
        self.partner_model = self.env["res.partner"]
        self.partner = self.env.ref("base.res_partner_1")

    def test_get_ws_params(self):
        wb = None
        data = None
        partners = self.partner_model.search([])
        ws_params = self.partner_export_xlsx._get_ws_params(wb, data, partners)
        self.assertIsInstance(ws_params, list)
        self.assertEqual(len(ws_params), 1)
        ws_param = ws_params[0]
        self.assertIsInstance(ws_param, dict)
        expected_keys = [
            "ws_name",
            "generate_ws_method",
            "title",
            "wanted_list",
            "col_specs",
        ]
        self.assertListEqual(list(ws_param.keys()), expected_keys)
        self.assertEqual(ws_param["ws_name"], "Partners")
        self.assertEqual(ws_param["generate_ws_method"], "_partner_report")
        self.assertEqual(ws_param["title"], "Partners")
        self.assertListEqual(
            ws_param["wanted_list"],
            ["name", "number_of_contacts", "is_company", "is_company_formula"],
        )
        col_specs = ws_param["col_specs"]
        self.assertIsInstance(col_specs, dict)
        expected_col_specs_keys = [
            "name",
            "number_of_contacts",
            "is_company",
            "is_company_formula",
        ]
        self.assertListEqual(list(col_specs.keys()), expected_col_specs_keys)
        self.assertIsInstance(col_specs["name"], dict)
        self.assertIsInstance(col_specs["number_of_contacts"], dict)
        self.assertIsInstance(col_specs["is_company"], dict)
        self.assertIsInstance(col_specs["is_company_formula"], dict)
        name_col_spec = col_specs["name"]
        self.assertEqual(name_col_spec["header"]["value"], "Name")
        self.assertEqual(name_col_spec["width"], 20)
        num_contacts_col_spec = col_specs["number_of_contacts"]
        self.assertEqual(num_contacts_col_spec["header"]["value"], "# Contacts")
        self.assertEqual(num_contacts_col_spec["width"], 10)
        is_company_col_spec = col_specs["is_company"]
        self.assertEqual(is_company_col_spec["header"]["value"], "Company")
        self.assertEqual(is_company_col_spec["width"], 10)
        is_company_formula_col_spec = col_specs["is_company_formula"]
        self.assertEqual(
            is_company_formula_col_spec["header"]["value"], "Company Y/N ?"
        )
        self.assertEqual(is_company_formula_col_spec["data"]["type"], "formula")
        self.assertEqual(is_company_formula_col_spec["width"], 14)
