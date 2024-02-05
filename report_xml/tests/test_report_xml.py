# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl).

import json

from lxml import etree

from odoo import http
from odoo.tests import common


class TestXmlReport(common.HttpCase):
    def test_xml(self):
        report_object = self.env["ir.actions.report"]
        report_name = "report_xml.demo_report_xml_view"
        report = report_object._get_report_from_name(report_name)
        docs = self.env["res.company"].search([], limit=1)
        self.assertEqual(report.report_type, "qweb-xml")
        result_report = report_object._render(report_name, docs.ids, {})
        result_tree = etree.fromstring(result_report[0])
        el = result_tree.xpath("/root/user/name")
        self.assertEqual(el[0].text, docs.ensure_one().name)

    def test_xml_extension(self):
        self.authenticate("admin", "admin")
        report_object = self.env["ir.actions.report"]
        report_name = "report_xml.demo_report_xml_view"
        report = report_object._get_report(report_name)
        # Test changing report to use ".svg" extension
        report.write({"xml_extension": "svg"})
        filename = self.get_report_headers().headers.get("Content-Disposition")
        self.assertTrue(".svg" in filename)
        # Test changing report to use ".ffdata" extension
        report.write({"xml_extension": "ffdata"})
        filename = self.get_report_headers().headers.get("Content-Disposition")
        self.assertTrue(".ffdata" in filename)

    def get_report_headers(self):
        return self.url_open(
            url="/report/download",
            data={
                "data": json.dumps(
                    ["/report/xml/report_xml.demo_report_xml_view/1", "qweb-xml"]
                ),
                "csrf_token": http.Request.csrf_token(self),
            },
        )
