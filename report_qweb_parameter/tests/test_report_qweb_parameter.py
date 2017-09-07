# -*- coding: utf-8 -*-
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import lxml.etree as ET

from odoo.addons.base.ir.ir_qweb import QWebException
from odoo.tests import common


class TestReportQWebParameter(common.TransactionCase):
    def test_qweb_parameter(self):
        report_name = 'report_qweb_parameter.test_report_length'
        docs = self.env['res.company'].search([], limit=1)
        country_us = self.env.ref('base.us')
        vat = docs.vat
        website = docs.website
        fax = docs.fax
        company_registry = docs.company_registry
        docs.update({
            'fax': '12345678901',
            'vat': '12345678901',
            'website': '1234567890',
            'country_id': country_us.id,
            'company_registry': '1234567890'
        })
        docs.check_report = True
        rep = self.env['report'].render(report_name, {'docs': docs})
        root = ET.fromstring(rep)
        self.assertEqual(root[1][0][0][0].text, "1234567890")
        self.assertEqual(root[1][0][0][2].text, "1234567890")
        docs.update({'fax': '123456789'})
        with self.assertRaises(QWebException):
            self.env['report'].render(report_name, {'docs': docs})
        docs.update({'fax': '1234567890', 'vat': '123456789'})
        with self.assertRaises(QWebException):
            self.env['report'].render(report_name, {'docs': docs})
        docs.update({'vat': '1234567890', 'website': '12345678901'})
        with self.assertRaises(QWebException):
            self.env['report'].render(report_name, {'docs': docs})
        docs.update(
            {'website': '1234567890', 'company_registry': '12345678901'})
        with self.assertRaises(QWebException):
            self.env['report'].render(report_name, {'docs': docs})
        docs.update({
            'fax': fax,
            'vat': vat,
            'website': website,
            'company_registry': company_registry
        })
