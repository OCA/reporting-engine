# Copyright 2021 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import tempfile
from contextlib import closing

from odoo import models

_logger = logging.getLogger(__name__)


class IrActionReport(models.Model):

    _inherit = "ir.actions.report"

    def _is_report_type_signable(self):
        res = super()._is_report_type_signable()
        return res or (self.report_type == "py3o")

    def render_py3o(self, res_ids, data):
        certificate = self._certificate_get(res_ids)
        content, filetype = super().render_py3o(res_ids, data)
        signed = ""
        if certificate:
            # Creating temporary origin PDF
            pdf_fd, pdf = tempfile.mkstemp(suffix=".pdf", prefix="report.tmp.")
            try:
                with closing(os.fdopen(pdf_fd, "wb")) as pf:
                    pf.write(content)
                _logger.debug(
                    "Signing PDF document '%s' for IDs %s with certificate '%s'",
                    self.report_name,
                    res_ids,
                    certificate.name,
                )
                signed = self.pdf_sign(pdf, certificate)
                # Read signed PDF
                if os.path.exists(signed):
                    with open(signed, "rb") as pf:
                        content = pf.read()
            finally:
                # Manual cleanup of the temporary files
                for fname in (pdf, signed):
                    try:
                        os.unlink(fname)
                    except (OSError, IOError):
                        _logger.error("Error when trying to remove file %s", fname)
        return content, filetype
