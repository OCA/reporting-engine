# Copyright 2023 fah-mili/Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):

    _inherit = "ir.actions.report"

    def _is_report_type_signable(self):
        res = super()._is_report_type_signable()
        return res or (self.report_type == "py3o" and self.py3o_filetype == "pdf")

    def _render_py3o(self, report_ref, res_ids, data=None):
        report = self._get_report(report_ref)
        certificate = self._certificate_get(report, res_ids)
        signed_content, ext = self._read_attached_signed_content(
            report, res_ids, certificate
        )
        if signed_content:
            return signed_content, "pdf"
        content, ext = super(IrActionsReport, self)._render_py3o(
            report_ref, res_ids, data
        )
        if certificate:
            content = self._sign_pdf_and_attach(res_ids, certificate, content)
        return content, ext
