# Copyright 2021 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os

from odoo import models

_logger = logging.getLogger(__name__)


class Py3oReport(models.TransientModel):
    _inherit = "py3o.report"

    def _postprocess_report(self, model_instance, result_path):
        report = self.ir_actions_report_id
        certificate = self.env["ir.actions.report"]._certificate_get(
            report, model_instance.ids
        )
        if not certificate:
            return super()._postprocess_report(model_instance, result_path)
        _logger.debug(
            "Signing PDF document '%s' for ID %s with certificate '%s'",
            report.report_name,
            model_instance.id,
            certificate.name,
        )
        signed = report.pdf_sign(result_path, certificate)
        try:
            os.unlink(result_path)
        except OSError:
            _logger.error("Error when trying to remove file %s", result_path)
        return super()._postprocess_report(model_instance, signed)
