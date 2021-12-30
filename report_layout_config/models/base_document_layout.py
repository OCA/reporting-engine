# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    full_header_img = fields.Binary(
        related="company_id.full_header_img",
        readonly=False,
        help="Replaces whole header with image",
    )
    full_footer_img = fields.Binary(
        related="company_id.full_footer_img",
        readonly=False,
        help="Replaces whole footer, disables footer logo",
    )

    @api.depends(
        "full_footer_img",
        "full_header_img",
    )
    def _compute_preview(self):
        super()._compute_preview()
