# Copyright 2021 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class IrActionReport(models.Model):
    _inherit = "ir.actions.report"

    def _is_report_type_signable(self):
        res = super()._is_report_type_signable()
        return res or (self.report_type == "py3o")
