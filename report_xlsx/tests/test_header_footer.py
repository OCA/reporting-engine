# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common
from odoo.exceptions import ValidationError
from cStringIO import StringIO
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class PartnerXlsx(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('sheet')
        sheet.write(0, 0, 'test')


class TestHeaderFooter(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestHeaderFooter, cls).setUpClass()
        cls.report = PartnerXlsx('report.res.partner.xlsx',
                                 'res.partner')

    def setUp(self):
        super(TestHeaderFooter, self).setUp()

        # Create Header
        self.header_001 = self.env['report.xlsx.hf'].create({
            'name': 'Header 001',
            'hf_type': 'header',
            'value': '&LPage &P of &N &CFilename: &F &RSheetname: &A',
        })
        # Create Footer
        self.footer_001 = self.env['report.xlsx.hf'].create({
            'name': 'Footer 001',
            'hf_type': 'footer',
            'value': '&LCurrent date: &D &RCurrent time: &T',
        })
        # Create Report
        self.report_xlsx = self.env['ir.actions.report.xml'].create({
            'report_name': 'res.partner.xlsx',
            'name': 'XLSX report',
            'report_type': 'xlsx',
            'model': 'res.partner',
            'header_id': self.header_001.id,
            'footer_id': self.footer_001.id,
        })

    def test_header_footer(self):
        """
        Check that the header and footer have been added to the worksheets
        """
        file_data = StringIO()
        partner = self.env['res.partner'].browse([1])
        workbook = self.report.create_workbook(
            file_data, {}, partner, self.report_xlsx)
        header = u'&LPage &P of &N &CFilename: &F &RSheetname: &A'
        footer = u'&LCurrent date: &D &RCurrent time: &T'

        for sheet in workbook.worksheets():
            self.assertEqual(header, sheet.header)
            self.assertEqual(footer, sheet.footer)

    def test_wrong_options(self):
        """
        Check that options must be a dict
        """
        with self.assertRaises(ValidationError):
            self.env['report.xlsx.hf'].create({
                'name': 'Header ERROR',
                'hf_type': 'header',
                'value': '&LPage &P of &N &CFilename: &F &RSheetname: &A',
                'manual_options': "1234",
            })

    def test_image_options(self):
        """
        Check that, adding image, modify the options
        """
        header = self.env['report.xlsx.hf'].create({
            'name': 'Header IMAGE',
            'hf_type': 'header',
            'value': '&L&G &C&G &R&G',
            'image_left':
                'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==',
            'image_left_name': 'image_left.jpg',
            'image_center':
                'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==',
            'image_center_name': 'image_center.jpg',
            'image_right':
                'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==',
            'image_right_name': 'image_right.jpg',
        })
        options = header.get_options()
        self.assertEqual(options.get('image_left'), 'image_left.jpg')
        self.assertEqual(options.get('image_center'), 'image_center.jpg')
        self.assertEqual(options.get('image_right'), 'image_right.jpg')
        self.assertTrue(options.get('image_data_left'))
        self.assertTrue(options.get('image_data_center'))
        self.assertTrue(options.get('image_data_right'))
