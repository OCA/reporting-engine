# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import xml.etree.ElementTree as ET

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestReportQWebParameter(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report_name = "test_report_length"
        cls.full_report_name = f"report_qweb_parameter.{cls.report_name}"
        cls.view = cls.env["ir.ui.view"].create(
            {
                "name": cls.report_name,
                "type": "qweb",
                "arch": """
                <data>
                    <li id="esc_length"
                        t-minlength="10"
                        t-length="10"
                        t-out="docs[0].street"
                        t-if="docs[0].street"/>
                    <li id="esc_conditional_length"
                        t-length="3"
                        t-out="docs[0].name or docs[0].company_registry"/>
                    <li id="esc_maxlength"
                        t-maxlength="10"
                        t-out="docs[0].website"
                        t-if="docs[0].website"/>
                    <li id="raw_length"
                        t-minlength="10"
                        t-length="10"
                        t-out="docs[0].vat"
                        t-if="docs[0].vat"/>
                    <li id="raw_conditional_length"
                        t-length="4"
                        t-out="docs[0].name or docs[0].company_registry"/>
                    <li id="raw_maxlength"
                        t-maxlength="10"
                        t-out="docs[0].company_registry"
                        t-if="docs[0].company_registry"/>
                    <li id="out_length"
                        t-minlength="10"
                        t-length="10"
                        t-out="docs[0].vat"
                        t-if="docs[0].vat"/>
                    <li id="out_conditional_length"
                        t-length="5"
                        t-out="docs[0].name or docs[0].company_registry"/>
                    <li id="out_maxlength"
                        t-maxlength="10"
                        t-out="docs[0].company_registry"
                        t-if="docs[0].company_registry"/>
                </data>
            """,
            }
        )
        cls.report = cls.env["ir.actions.report"].create(
            {
                "name": "Length Report",
                "model": "res.company",
                "report_type": "qweb-html",
                "report_name": cls.full_report_name,
            }
        )
        cls.env["ir.model.data"].create(
            [
                {
                    "module": "report_qweb_parameter",
                    "name": cls.report_name,
                    "model": "ir.ui.view",
                    "res_id": cls.view.id,
                },
                {
                    "module": "report_qweb_parameter",
                    "name": "test_report_length_report",
                    "model": "ir.actions.report",
                    "res_id": cls.report.id,
                },
            ]
        )

    def test_qweb_parameter(self):
        docs = self.env["res.company"].create(
            {
                "name": "Test company",
                "street": "12345678901",
                "vat": "12345678901",
                "company_registry": "1234567890",
            }
        )
        docs.website = "1234567890"
        rep = self.report._render(self.full_report_name, docs.ids, False)
        root = ET.fromstring(rep[0])

        # test length
        self.assertEqual(root[0].text, "1234567890")
        self.assertEqual(root[3].text, "1234567890")
        self.assertEqual(root[6].text, "1234567890")

        # test conditional length
        self.assertEqual(root[1].text, "Tes")
        self.assertEqual(root[4].text, "Test")
        self.assertEqual(root[7].text, "Test ")

        # test maxlength
        docs.update({"street": "123456789"})
        with self.assertRaises(ValidationError):
            self.report._render(self.full_report_name, docs.ids, False)
        docs.update({"street": "1234567890", "vat": "123456789"})
        with self.assertRaises(ValidationError):
            self.report._render(self.full_report_name, docs.ids, False)
        docs.update({"vat": "1234567890", "website": "12345678901"})
        with self.assertRaises(ValidationError):
            self.report._render(self.full_report_name, docs.ids, False)
        docs.update({"website": "1234567890", "company_registry": "12345678901"})
        with self.assertRaises(ValidationError):
            self.report._render(self.full_report_name, docs.ids, False)
