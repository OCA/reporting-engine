# Copyright 2021 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os

from odoo import models

_logger = logging.getLogger(__name__)


class Py3oReport(models.TransientModel):
    _inherit = "py3o.report"

    def _postprocess_report(self, model_instance, result_path):
        certificate = self.ir_actions_report_id._certificate_get(model_instance.ids)
        if not certificate:
            return super()._postprocess_report(model_instance, result_path)
        _logger.debug(
            "Signing PDF document '%s' for ID %s with certificate '%s'",
            self.ir_actions_report_id.report_name,
            model_instance.id,
            certificate.name,
        )
        signed = self.ir_actions_report_id.pdf_sign(result_path, certificate)
        try:
            os.unlink(result_path)
        except (OSError, IOError):
            _logger.error("Error when trying to remove file %s", result_path)
        return super()._postprocess_report(model_instance, signed)
