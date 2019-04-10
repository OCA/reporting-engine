# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models, exceptions, _
import logging

logger = logging.getLogger(__name__)


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    pdf_watermark = fields.Binary('Watermark')
    pdf_watermark_scale = fields.Boolean(
        string='Scale watermark?',
        help='Scales the watermark to be the same size as the report printed.')
    pdf_watermark_expression = fields.Char(
        'Watermark expression', help='An expression yielding the base64 '
        'encoded data to be used as watermark. \n'
        'You have access to variables `env` and `docs`')

    @api.constrains('pdf_watermark')
    def _check_pdf_watermark(self):
        if self.pdf_watermark:
            try:
                pdf = self.env['report']._read_watermark(self)
                if not pdf.numPages:
                    raise IOError
                if pdf.numPages > 1:
                    logger.debug(
                        'Your watermark contains more than one page '
                        'all but the first one will be ignored.',
                    )
            except IOError:
                raise exceptions.ValidationError(_(
                    'Could not set watermark.'
                    'Make sure that the watermark is either a PDF or '
                    'an Image file '
                    'and it contains at least a single page.'))
