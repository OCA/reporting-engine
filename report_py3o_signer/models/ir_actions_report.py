# Copyright 2023 fah-mili/Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models

import logging
_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):

    _inherit = 'ir.actions.report'

    def _signable_report(self):
        """Necessary to get the certificate with py3o reports"""
        is_py3o_signable = self.report_type == 'py3o' and self.py3o_filetype == 'pdf'
        return is_py3o_signable or super()._signable_report()

    def render_py3o(self, res_ids=None, data=None):
        certificate = self._certificate_get(res_ids)
        signed_content, ext = self._read_attached_signed_content(res_ids, certificate)
        if signed_content:
            return signed_content, 'pdf'
        content, ext = super(IrActionsReport, self).render_py3o(res_ids, data)
        if certificate:
            content = self._sign_pdf_and_attach(res_ids, certificate, content)
        return content, ext
