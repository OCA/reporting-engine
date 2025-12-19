# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    address_details = fields.Text(
        compute="_compute_address_details",
        store=True,
        readonly=False,
        translate=True,
        help="Custom address format used in reports and portal pages. "
        "When set, this replaces the standard address format for external display.",
    )

    @api.depends("parent_id.address_details", "type")
    def _compute_address_details(self):
        for partner in self:
            if partner.parent_id and partner.type == "contact":
                partner.address_details = partner.parent_id.address_details
                # No translation sync here to avoid unnecessary DB operations

    @api.model
    def _address_fields(self):
        """For address_details to be synced from parent."""
        return super()._address_fields() + ["address_details"]

    def _fields_sync(self, values):
        """Copy address_details translations from parent for contacts."""
        result = super()._fields_sync(values)
        parent = self.parent_id
        if parent and self.type == "contact" and parent.address_details:
            # Copy JSONB translations directly to avoid recursion
            self.env.cr.execute(
                """
                UPDATE res_partner
                SET address_details = p.address_details
                FROM res_partner p
                WHERE res_partner.id = %(partner_id)s
                AND p.id = %(parent_id)s
                """,
                {"partner_id": self.id, "parent_id": parent.id},
            )
        return result

    def _prepare_display_address(self, without_company=False):
        self.ensure_one()
        address_format, args = super()._prepare_display_address(
            without_company=without_company
        )
        if self.address_details:
            address_format = self.address_details
        return address_format, args
