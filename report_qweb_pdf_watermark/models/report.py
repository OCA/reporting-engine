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
try:
    from papersize import parse_couple, SIZES
except ImportError:
    raise
from openerp import api, models, tools
logger = getLogger(__name__)


class Report(models.Model):
    _inherit = 'report'

    @api.multi
    def _scale_watermark(self, report, image):
        _format = report.paperformat_id.format.lower()
        if _format == 'custom':
            size = \
                int(report.paperformat_id.page_height), \
                int(report.paperformat_id.page_width)
        else:
            try:
                size = parse_couple(SIZES[_format])
                size = int(size[0]), int(size[1])
            except KeyError:
                logger.warning(
                    'Scaling the watermark failed.'
                    'Could not extract paper dimensions for %s' % (_format))
        return image.resize(size, resample=Image.LANCZOS)

    @api.multi
    def _read_watermark(self, report, ids=None):
        if report.pdf_watermark:
            watermark = b64decode(report.pdf_watermark)
        else:
            watermark = tools.safe_eval(
                report.pdf_watermark_expression or 'None',
                dict(
                    env=self.env,
                    docs=self.env[report.model].browse(ids),
                )
            )
            if watermark:
                watermark = b64decode(watermark)
        if not watermark:
            return
        try:
            pdf_watermark = PdfFileReader(StringIO(watermark))
        except PdfReadError:
            image = Image.open(StringIO(watermark))
            pdf_buffer = StringIO()
            if image.mode != 'RGB':
                image = image.convert('RGB')
            if report.paperformat_id.format and \
                    report.paperformat_id.format.lower() in SIZES and \
                    report.pdf_watermark_scale:
                image = self._scale_watermark(report, image)
            image.save(pdf_buffer, 'pdf', quality=100)
            pdf_watermark = PdfFileReader(pdf_buffer)
        return pdf_watermark

    @api.model
    def get_pdf(self, ids, report_name, html=None, data=None):
        report = self._get_report_from_name(report_name)
        result = super(Report, self).get_pdf(
            self.env[report.model].browse(ids),
            report_name,
            html=html,
            data=data,
        )
        pdf_watermark = self._read_watermark(report, ids)
        if not pdf_watermark:
            return result
        pdf = PdfFileWriter()
        for page in PdfFileReader(StringIO(result)).pages:
            watermark_page = pdf.addBlankPage(
                page.mediaBox.getWidth(), page.mediaBox.getHeight()
            )
            watermark_page.mergePage(pdf_watermark.getPage(0))
            watermark_page.mergePage(page)

        pdf_content = StringIO()
        pdf.write(pdf_content)
        return pdf_content.getvalue()
