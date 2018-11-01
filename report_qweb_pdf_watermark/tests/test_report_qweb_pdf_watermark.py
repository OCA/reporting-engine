# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import functools
import logging
from StringIO import StringIO
from timeit import timeit
from pyPdf import PdfFileReader, PdfFileWriter
try:
    from pdfrw import PdfReader, PdfWriter
except ImportError:
    PdfReader = PdfFileReader
from PIL import Image
from openerp.tests.common import HttpCase
from ..models import report
_logger = logging.getLogger(__name__)


class TestReportQwebPdfWatermark(HttpCase):
    def test_report_qweb_pdf_watermark(self):
        Image.init()
        # with our image, we have three
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

    def _get_pdf(self):
        return self.registry['report'].get_pdf(
            self.cr,
            self.uid,
            self.env['res.users'].search([]).ids,
            'report_qweb_pdf_watermark.demo_report_view',
            context={}
        )

    def _test_report_images(self, number):
        pdf = self._get_pdf()
        self.assertEqual(pdf.count('/Subtype /Image'), number)

    def test_page_merge_performance(self):
        pdf = self._get_pdf()
        merge_pypdf = functools.partial(
            self.env['report']._merge_pdfs_pypdf,
            PdfFileReader(StringIO(pdf)), PdfFileReader(StringIO(pdf))
        )
        merge_pdfrw = functools.partial(
            self.env['report']._merge_pdfs_pdfrw,
            PdfReader(StringIO(pdf)), PdfReader(StringIO(pdf))
        )
        # patch import to match what we're doing
        report.PdfFileWriter = PdfFileWriter
        _logger.info(
            'PDF merge using pypdf: %f', timeit(merge_pypdf, number=10),
        )
        report.PdfFileWriter = PdfWriter
        _logger.info(
            'PDF merge using pdfrw: %f', timeit(merge_pdfrw, number=10),
        )
