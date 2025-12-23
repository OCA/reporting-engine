# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    address_details = fields.Text(
        translate=True,
        help="Custom address format used in reports and portal pages. "
        "When set, this replaces the standard address format for external display.",
    )

    def _prepare_display_address(self, without_company=False):
        self.ensure_one()
        address_format, args = super()._prepare_display_address(
            without_company=without_company
        )
        if self.address_details:
            address_format = self.address_details
        return address_format, args
