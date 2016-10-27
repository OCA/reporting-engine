# -*- coding: utf-8 -*-
# Copyright 2015 bloopark systems (<http://bloopark.de>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from PIL import Image
from io import BytesIO
from openerp.tests import common


class TestReport(common.TransactionCase):
    at_install = False
    post_install = True

    def setUp(self):
        """Test setUp."""
        super(TestReport, self).setUp()
        self.report = self.env['report']

    def test_00_barcode_report(self):
        """----- Test if the function is generating CODE128 and the color."""
        type = 'code128'
        value = 'test'
        kw = {
            'elaphe': '1',
            'scale': '2.0',
            'barmargin': '1',
            'extraopts': 'backgroundcolor:FFFF00'
        }
        barcode = self.report.generate_barcode(type, value, kw, 0, 0)
        im = Image.open(BytesIO(barcode))
        rgb_im = im.convert('RGB')
        r, g, b = rgb_im.getpixel((1, 1))
        self.assertEqual(r, 255)
        self.assertEqual(g, 255)
        self.assertEqual(b, 0)

        kw = {
            'elaphe': '1',
            'scale': '2.0',
            'barmargin': '1',
            'extraopts': 'backgroundcolor:0000FF'
        }
        barcode = self.report.generate_barcode(type, value, kw, 0, 0)
        im = Image.open(BytesIO(barcode))
        rgb_im = im.convert('RGB')
        r, g, b = rgb_im.getpixel((1, 1))
        self.assertEqual(r, 0)
        self.assertEqual(g, 0)
        self.assertEqual(b, 255)

    def test_01_barcode_report(self):
        """----- Test the size of barcode."""
        type = 'code128'
        value = 'test'
        kw = {
            'elaphe': '1',
            'scale': '2.0',
            'barmargin': '1',
            'extraopts': 'backgroundcolor:FFFF00'
        }
        barcode = self.report.generate_barcode(type, value, kw, 0, 0)
        im = Image.open(BytesIO(barcode))
        width, height = im.size
        self.assertEqual(width, 140)
        self.assertEqual(height, 148)

        kw = {
            'elaphe': '1',
            'scale': '4.0',
            'barmargin': '1',
            'extraopts': 'backgroundcolor:FFFF00'
        }
        barcode = self.report.generate_barcode(type, value, kw, 0, 0)
        im = Image.open(BytesIO(barcode))
        width, height = im.size
        self.assertEqual(width, 280)
        self.assertEqual(height, 296)
