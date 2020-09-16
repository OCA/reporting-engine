# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
import logging
from io import BytesIO

_logger = logging.getLogger(__name__)
try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError as err:
    _logger.debug(err)


class IrActionsReport(models.Model):

    _inherit = 'ir.actions.report'

    encrypt = fields.Boolean()

    def render_qweb_pdf(self, res_ids=None, data=None):
        document, type = super(IrActionsReport, self).render_qweb_pdf(
            res_ids=res_ids, data=data)
        if self.encrypt and self.env.context.get('encrypt_password', False):
            output_pdf = PdfFileWriter()
            in_buff = BytesIO(document)
            pdf = PdfFileReader(in_buff)
            output_pdf.appendPagesFromReader(pdf)
            output_pdf.encrypt(self.env.context.get('encrypt_password'))
            buff = BytesIO()
            output_pdf.write(buff)
            document = buff.getvalue()
        return document, type
