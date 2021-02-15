# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import os

from PIL import Image
from openerp.tests.common import HttpCase


class TestReportQwebPdfWatermark(HttpCase):
    def test_report_qweb_pdf_watermark(self):
        Image.init()
        # with our image, we have three

        logo = self.env.user.company_id.logo
        if not logo:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(dir_path, '../static/description/icon.png')
            fn = open(file_path, 'r')
            self.env.user.company_id.logo = base64.encodestring(fn.read())
            fn.close()

        self._test_report_images(3)

        self.env.ref('report_qweb_pdf_watermark.demo_report').write({
            'pdf_watermark_expression': False,
        })
        # without, we have two
        self._test_report_images(2)

        self.env.ref('report_qweb_pdf_watermark.demo_report').write({
            'pdf_watermark': self.env.user.company_id.logo,
        })
        # and now we should have three again
        self._test_report_images(3)

    def _test_report_images(self, number):
        pdf = self.registry['report'].get_pdf(
            self.cr,
            self.uid,
            self.env['res.users'].search([]).ids,
            'report_qweb_pdf_watermark.demo_report_view',
            context={}
        )
        self.assertEqual(pdf.count('/Subtype /Image'), number)
