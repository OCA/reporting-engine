# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    full_header_img = fields.Binary(
        related="company_id.full_header_img", readonly=False
    )
    full_footer_img = fields.Binary(
        related="company_id.full_footer_img", readonly=False
    )

    need_images_layout = fields.Boolean(
        compute="_compute_need_images_layout", readonly=True
    )

    @api.depends("report_layout_id")
    def _compute_need_images_layout(self):
        self.ensure_one()
        img_lay = self.env.ref("report_layout_config.external_layout_images").view_id
        self.need_images_layout = self.external_report_layout_id == img_lay

    @api.depends(
        "full_footer_img",
        "full_header_img",
    )
    def _compute_preview(self):
        super()._compute_preview()
