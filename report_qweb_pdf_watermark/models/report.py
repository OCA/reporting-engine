# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from base64 import b64decode
from logging import getLogger
from PIL import Image
from io import BytesIO

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass
from odoo import api, models, fields, tools

logger = getLogger(__name__)

try:
    from PyPDF2 import PdfFileWriter, PdfFileReader  # pylint: disable=W0404
    from PyPDF2.utils import PdfReadError  # pylint: disable=W0404
except ImportError:
    logger.debug('Can not import PyPDF2')


class Report(models.Model):
    _inherit = 'ir.actions.report'

    pdf_watermark = fields.Binary('Watermark')
    pdf_watermark_expression = fields.Char(
        'Watermark expression', help='An expression yielding the base64 '
        'encoded data to be used as watermark. \n'
        'You have access to variables `env` and `docs`')

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        if not self.env.context.get('res_ids'):
            return super(
                Report, self.with_context(res_ids=res_ids)
            ).render_qweb_pdf(res_ids=res_ids, data=data)
        return super(Report, self).render_qweb_pdf(res_ids=res_ids, data=data)

    @api.model
    def _run_wkhtmltopdf(self, bodies, header=None, footer=None,
                         landscape=False, specific_paperformat_args=None,
                         set_viewport_size=False):
        result = super(Report, self)._run_wkhtmltopdf(
            bodies, header=header, footer=footer, landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size)

        docids = self.env.context.get('res_ids', False)
        watermark = None
        if self.pdf_watermark:
            watermark = b64decode(self.pdf_watermark)
        elif docids:
            watermark = tools.safe_eval(
                self.pdf_watermark_expression or 'None',
                dict(env=self.env, docs=self.env[self.model].browse(docids)),
            )
            if watermark:
                watermark = b64decode(watermark)

        if not watermark:
            return result

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
            return result

        if pdf_watermark.numPages < 1:
            logger.error('Your watermark pdf does not contain any pages')
            return result
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

        return pdf_content.getvalue()
