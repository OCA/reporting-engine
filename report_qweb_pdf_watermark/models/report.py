# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import math
from StringIO import StringIO
from base64 import b64decode
from logging import getLogger

from PIL import Image
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
from openerp import api, models, tools

logger = getLogger(__name__)

paper_mm = {
    u'A4': (210, 297)
}


class Report(models.Model):
    _inherit = 'report'

    @api.v7
    def get_pdf(self, cr, uid, ids, report_name, html=None, data=None, context=None):
        # pylint: disable=R8110
        # this override cannot be done in v8 api
        result = super(Report, self).get_pdf(
            cr, uid, ids, report_name, html=html, data=data,
            context=context
        )

        report, watermark = self.get_watermark(cr, uid, ids, report_name, context)

        if not watermark:
            return result

        pdf = PdfFileWriter()
        pdf_watermark = None
        try:
            pdf_watermark = PdfFileReader(StringIO(watermark))
        except PdfReadError:
            # let's see if we can convert this with pillow
            try:
                image = Image.open(StringIO(watermark))
                pdf_buffer = StringIO()
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                dpi = image.info.get(
                    'dpi', report.paperformat_id.dpi or 300
                )
                if isinstance(dpi, tuple):
                    dpi = dpi[0]

                # resizing image based paper format millimeters
                # formula: dpi * mm * 0,0393701 inches
                mm = paper_mm.get(report.paperformat_id.format)
                if mm:
                    image_dimension = tuple(
                        int(math.ceil(dim * dpi * 0.0393701)) for dim in mm
                    )
                    image = image.resize(image_dimension, Image.ANTIALIAS)

                image.save(pdf_buffer, 'pdf', resolution=dpi)
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

    def get_watermark(self, cr, uid, ids, report_name, context):
        """
        by default the watermark is getting from report. inherit to change this
        behaviour
        """
        report = self._get_report_from_name(cr, uid, report_name)
        if report.pdf_watermark:
            watermark = b64decode(report.pdf_watermark)
        else:
            env = api.Environment(cr, uid, context)
            watermark = tools.safe_eval(
                report.pdf_watermark_expression or 'None',
                dict(env=env, docs=env[report.model].browse(ids)),
            )
            if watermark:
                watermark = b64decode(watermark)
        return report, watermark
