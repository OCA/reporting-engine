# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    zip_download = fields.Boolean(
        help="If enabled, the report will be downloaded as a zip "
        "file for multiple records."
    )
