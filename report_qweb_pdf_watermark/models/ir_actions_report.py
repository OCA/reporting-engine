# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from base64 import b64decode
from logging import getLogger
from PIL import Image
from io import BytesIO

from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.utils import PdfReadError

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass
from odoo import api, fields, models, tools

logger = getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    pdf_watermark = fields.Binary('Watermark')
    pdf_watermark_expression = fields.Char(
        'Watermark expression', help='An expression yielding the base64 '
        'encoded data to be used as watermark. \n'
        'You have access to variables `env` and `docs`')

    @api.model
    def render_qweb_pdf(self, res_ids=None, data=None):
        result, format = super(IrActionsReport, self).render_qweb_pdf(
            res_ids=res_ids, data=data)
        watermark = None
        if self.pdf_watermark:
            watermark = b64decode(self.pdf_watermark)
        elif self.pdf_watermark_expression:
            watermark = tools.safe_eval(
                self.pdf_watermark_expression,
                dict(env=self.env, docs=self.env[self.model].browse(res_ids)),
            )
            if watermark:
                watermark = b64decode(watermark)

        if not watermark:
            return result, format

        pdf = PdfFileWriter()
        pdf_watermark = None
        try:
            pdf_watermark = PdfFileReader(BytesIO(watermark))
        except PdfReadError:
            # let's see if we can convert this with pillow
            try:
                Image.init()
                image = Image.open(BytesIO(watermark))
                pdf_buffer = BytesIO()
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                resolution = image.info.get(
                    'dpi', self.paperformat_id.dpi or 90
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
            return result, format

        if pdf_watermark.numPages < 1:
            logger.error('Your watermark pdf does not contain any pages')
            return result, format
        if pdf_watermark.numPages > 1:
            logger.debug('Your watermark pdf contains more than one page, '
                         'all but the first one will be ignored')

        for page in PdfFileReader(BytesIO(result)).pages:
            watermark_page = pdf.addBlankPage(
                page.mediaBox.getWidth(), page.mediaBox.getHeight()
            )
            watermark_page.mergePage(pdf_watermark.getPage(0))
            watermark_page.mergePage(page)

        pdf_content = BytesIO()
        pdf.write(pdf_content)

        return pdf_content.getvalue(), format
