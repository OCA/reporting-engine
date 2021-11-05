# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl).

from lxml import etree

from odoo.tests import common


class TestXmlReport(common.TransactionCase):
    def test_xml(self):
        report_object = self.env["ir.actions.report"]
        report_name = "report_xml.demo_report_xml_view"
        report = report_object._get_report_from_name(report_name)
        docs = self.env["res.company"].search([], limit=1)
        self.assertEqual(report.report_type, "qweb-xml")
        result_report = report._render(docs.ids, {})
        result_tree = etree.fromstring(result_report[0])
        el = result_tree.xpath("/root/user/name")
        self.assertEqual(el[0].text, docs.ensure_one().name)
