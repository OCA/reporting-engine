# Copyright (C) 2015 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestExportSqlQuery(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sql_export_obj = cls.env["sql.export"]
        cls.wizard_obj = cls.env["sql.file.wizard"]
        # Do not rely on demo data: OCA CI runs tests without it.
        cls.sql_report_demo = cls.sql_export_obj.create(
            {
                "name": "Export Partners (Test)",
                "query": "SELECT name, street\nFROM res_partner;",
            }
        )
        cls.sql_report_demo.button_validate_sql_expression()

    def test_sql_query(self):
        wizard = self.wizard_obj.create(
            {
                "sql_export_id": self.sql_report_demo.id,
            }
        )
        wizard.export_sql()
        export = base64.b64decode(wizard.binary_file).decode("utf-8")
        self.assertEqual(export.split(";")[0], "name")
        self.assertTrue(len(export.split(";")) > 6)

    def test_prohibited_queries(self):
        prohibited_queries = [
            "upDaTe res_partner SET name = 'test' WHERE id = 1",
            "DELETE FROM sql_export WHERE name = 'test';",
            "  DELETE FROM sql_export WHERE name = 'test'   ;",
            """DELETE
            FROM
            sql_export
            WHERE name = 'test'
            """,
        ]
        for query in prohibited_queries:
            with self.assertRaises(UserError):
                sql_export = self.sql_export_obj.create(
                    {"name": "test_prohibited", "query": query}
                )
                sql_export.button_validate_sql_expression()

    def test_authorized_queries(self):
        authorized_queries = [
            "SELECT create_date FROM res_partner",
        ]

        for query in authorized_queries:
            sql_export = self.sql_export_obj.create(
                {"name": "test_authorized", "query": query}
            )
            sql_export.button_validate_sql_expression()
            self.assertEqual(
                sql_export.state, "sql_valid", f"{query} is a valid request"
            )

    def test_sql_query_with_params(self):
        # Do not rely on demo data: OCA CI runs tests without it.
        query = self.sql_export_obj.create(
            {
                "name": "Export Partners With Variables (Test)",
                "query": (
                    "SELECT p.id\n"
                    "FROM res_partner p\n"
                    "LEFT JOIN res_partner_res_partner_category_rel rel\n"
                    "    ON rel.partner_id = p.id\n"
                    "WHERE create_date > %(Date)s\n"
                    "AND id = %(ID)s\n"
                    "AND rel.category_id in %(Categories)s\n"
                ),
                "query_properties_definition": [
                    {
                        "name": "630eca383bc142e6",
                        "type": "date",
                        "string": "Date",
                    },
                    {
                        "name": "907ac618eccbab74",
                        "type": "integer",
                        "string": "ID",
                    },
                    {
                        "name": "ec0556e22932334b",
                        "string": "Categories",
                        "type": "many2many",
                        "default": False,
                        "comodel": "res.partner.category",
                        "domain": False,
                    },
                ],
            }
        )
        query.write({"state": "sql_valid"})
        categ_id = (
            self.env["res.partner.category"].create({"name": "Consulting Services"}).id
        )
        wizard = self.wizard_obj.create(
            {
                "sql_export_id": query.id,
            }
        )
        wizard.write(
            {
                "query_properties": [
                    {
                        "name": "630eca383bc142e6",
                        "string": "Date",
                        "type": "date",
                        "default": "",
                        "value": "2023-02-03",
                    },
                    {
                        "name": "ec0556e22932334b",
                        "string": "Categories",
                        "type": "many2many",
                        "default": False,
                        "comodel": "res.partner.category",
                        "domain": False,
                        "value": [[categ_id, "Consulting Services"]],
                    },
                    {
                        "name": "907ac618eccbab74",
                        "string": "ID",
                        "type": "integer",
                        "default": False,
                        "value": 1,
                    },
                ]
            }
        )
        wizard.export_sql()
        export = base64.b64decode(wizard.binary_file)
        self.assertTrue(export)
