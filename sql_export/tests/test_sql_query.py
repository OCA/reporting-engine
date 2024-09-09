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
        cls.sql_report_demo = cls.env.ref("sql_export.sql_export_partner")

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
                sql_export.state, "sql_valid", "%s is a valid request" % (query)
            )

    def test_sql_query_with_params(self):
        query = self.env.ref("sql_export.sql_export_partner_with_variables")
        query.write({"state": "sql_valid"})
        categ_id = self.env.ref("base.res_partner_category_0").id
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

    def test_keep_generated_file(self):
        """Test that we keep generated files"""
        self.sql_report_demo.keep_generated_file = True
        wizard = self.wizard_obj.create(
            {
                "sql_export_id": self.sql_report_demo.id,
            }
        )
        wizard.export_sql()
        attachment = wizard._get_field_attachment()
        wizard.sudo().unlink()
        self.assertTrue(attachment.exists())
