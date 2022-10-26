# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import xml.etree.ElementTree as ET

from odoo.tests import common

from odoo.addons.base.models.ir_qweb import QWebException


class TestReportQWebParameter(common.TransactionCase):
    def test_qweb_parameter(self):
        report_name = "report_qweb_parameter.test_report_length"
        report_obj = self.env["ir.actions.report"]
        report_object = report_obj
        docs = self.env["res.company"].create(
            {
                "name": "Test company",
                "street": "12345678901",
                "vat": "12345678901",
                "company_registry": "1234567890",
            }
        )
        docs.website = "1234567890"  # for avoding that Odoo adds http://
        rep = report_object._render(report_name, docs.ids, False)
        root = ET.fromstring(rep[0])
        self.assertEqual(root[0].text, "1234567890")
        self.assertEqual(root[2].text, "1234567890")
        self.assertEqual(root[4].text, "1234567890")
        docs.update({"street": "123456789"})
        with self.assertRaises(QWebException):
            report_object._render(report_name, docs.ids, False)
        docs.update({"street": "1234567890", "vat": "123456789"})
        with self.assertRaises(QWebException):
            report_object._render(report_name, docs.ids, False)
        docs.update({"vat": "1234567890", "website": "12345678901"})
        with self.assertRaises(QWebException):
            report_object._render(report_name, docs.ids, False)
        docs.update({"website": "1234567890", "company_registry": "12345678901"})
        with self.assertRaises(QWebException):
            report_object._render(report_name, docs.ids, False)
