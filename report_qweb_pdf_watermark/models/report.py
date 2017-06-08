# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from base64 import b64decode
from logging import getLogger
from PIL import Image
from StringIO import StringIO

from pyPdf import PdfFileWriter, PdfFileReader
from pyPdf.utils import PdfReadError
try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
    from PyPDF2.utils import PdfReadError  # pylint: disable=W0404
except ImportError:
    pass
try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass
from odoo import api, models, tools

logger = getLogger(__name__)


class Report(models.Model):
    _inherit = 'report'

    @api.model
    def get_pdf(self, docids, report_name, html=None, data=None):
        result = super(Report, self).get_pdf(
            docids, report_name, html=html, data=data)
        report = self._get_report_from_name(report_name)
        watermark = None
        if report.pdf_watermark:
            watermark = b64decode(report.pdf_watermark)
        else:
            watermark = tools.safe_eval(
                report.pdf_watermark_expression or 'None',
                dict(env=self.env, docs=self.env[report.model].browse(docids)),
            )
            if watermark:
                watermark = b64decode(watermark)

        if not watermark:
            return result

        pdf = PdfFileWriter()
        pdf_watermark = None
        try:
            pdf_watermark = PdfFileReader(StringIO(watermark))
        except PdfReadError:
            # let's see if we can convert this with pillow
            try:
                Image.init()
                image = Image.open(StringIO(watermark))
                pdf_buffer = StringIO()
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                resolution = image.info.get(
                    'dpi', report.paperformat_id.dpi or 90
                )
                if isinstance(resolution, tuple):
                    resolution = resolution[0]
                image.save(pdf_buffer, 'pdf', resolution=resolution)
                pdf_watermark = PdfFileReader(pdf_buffer)
            except:
                logger.exception('Failed to load watermark')

        if not pdf_watermark:
            logger.error(
                'No usable watermark found, got %s...', watermark[:100]
            )
            return result

        if pdf_watermark.numPages < 1:
            logger.error('Your watermark pdf does not contain any pages')
            return result
        if pdf_watermark.numPages > 1:
            logger.debug('Your watermark pdf contains more than one page, '
                         'all but the first one will be ignored')

        for page in PdfFileReader(StringIO(result)).pages:
            watermark_page = pdf.addBlankPage(
                page.mediaBox.getWidth(), page.mediaBox.getHeight()
            )
            watermark_page.mergePage(pdf_watermark.getPage(0))
            watermark_page.mergePage(page)

        pdf_content = StringIO()
        pdf.write(pdf_content)

        return pdf_content.getvalue()
