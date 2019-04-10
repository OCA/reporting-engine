# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from PIL import Image
from openerp.tests.common import HttpCase
from openerp import SUPERUSER_ID, exceptions

# Subtype is a required field of an XObject and when it's Image we are dealing
# with an image. (apparently there is no way for us to to a `pdf.getImages()`)
SUBTYPE_IMAGE = '/Subtype /Image'


class TestReportQwebPdfWatermark(HttpCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestReportQwebPdfWatermark, self).setUp()
        self.report_model = self.env['report']
        self.report = self.env.ref(
            'report_qweb_pdf_watermark.demo_report')
        Image.init()

    def _clean_watermark(self, report):
        report.write({
            'pdf_watermark': None,
            'pdf_watermark_expression': None,
        })

    def test_print_report(self):
        """ Load the report as it was defined and verify the contents and the
        pages.
        """
        pdf = self.env['report'].get_pdf(SUPERUSER_ID, self.report.report_name)
        # The pdf should have only our watermark as it's image.
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 1)

    def test_print_watermarked(self):
        """ Load the report as it was defined add a watermark and verify the
        contents and the pages.
        """
        self._clean_watermark(self.report)
        pdf = self.env['report'].get_pdf(SUPERUSER_ID, self.report.report_name)
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 0)
        self.report.write({'pdf_watermark': self.env.user.company_id.logo})
        pdf = self.env['report'].get_pdf(SUPERUSER_ID, self.report.report_name)
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 1)

    def test_print_watermarked_expression(self):
        """ Load the report as it was defined and use a valid watermark
        expression in order to fetch the watermark.
        """
        self._clean_watermark(self.report)
        pdf = self.env['report'].get_pdf(SUPERUSER_ID, self.report.report_name)
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 0)
        self.report.write({
            'pdf_watermark_expression': 'docs[0].company_id.logo',
        })
        pdf = self.env['report'].get_pdf(SUPERUSER_ID, self.report.report_name)
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 1)

    def test_print_watermarked_error(self):
        """ Load the report as it was defined and use an invalid watermark"""
        self._clean_watermark(self.report)
        pdf = self.env['report'].get_pdf(SUPERUSER_ID, self.report.report_name)
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 0)
        with self.assertRaises(exceptions.ValidationError):
            self.report.write({'pdf_watermark': 'test'})
            self.env['report'].get_pdf(SUPERUSER_ID, self.report.report_name)

    def test_print_watermark_expression_error(self):
        """ Use a wrong watermark expression and one that does not return
        neither a pdf nor an Image and verify correct behaviour.
        """
        self._clean_watermark(self.report)
        pdf = self.report_model.get_pdf(SUPERUSER_ID, self.report.report_name)
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 0)
        self.report.write({'pdf_watermark_expression': 'tabs over spaces'})
        with self.assertRaises(SyntaxError):
            self.report_model.get_pdf(SUPERUSER_ID, self.report.report_name)

    def test_get_pdf(self):
        """ Call get_pdf using the old and the new api."""
        pdf = self.report_model.get_pdf(SUPERUSER_ID, self.report.report_name)
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 1)
        pdf = self.registry['report'].get_pdf(
            self.env.cr,
            self.env.uid,
            [SUPERUSER_ID],
            'report_qweb_pdf_watermark.demo_report_view',
        )
        self.assertEquals(pdf.count(SUBTYPE_IMAGE), 1)
