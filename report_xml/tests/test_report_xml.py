# -*- coding: utf-8 -*-
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo.tests import common


class TestXmlReport(common.TransactionCase):
    def test_xml(self):
        report_object = self.env['ir.actions.report.xml']
        report_name = 'report_xml.demo_report_xml_view'
        self.assertEqual(
            report_name, report_object._lookup_report(report_name))
        docs = self.env['res.company'].search([], limit=1)
        rep = report_object.render_report(
            docs.ids, report_name, {}
        )
        root = etree.fromstring(rep[0])
        el = root.xpath('/root/user/name')
        self.assertEqual(
            el[0].text,
            docs.ensure_one().name
        )
