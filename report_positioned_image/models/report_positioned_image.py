# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from io import BytesIO

from PIL import Image

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReportPositionedImage(models.Model):
    _name = "report.positioned.image"
    _description = "Report Positioned Image"

    name = fields.Char(required=True)
    image = fields.Binary(attachment=True, required=True)
    pos_top = fields.Float(string="Top (mm)", default=5.0)
    pos_left = fields.Float(string="Left (mm)", default=5.0)
    width = fields.Float(string="Width (mm)")
    height = fields.Float(string="Height (mm)")
    respect_image_ratio = fields.Boolean(
        default=True,
        help="When enabled, changing width or height will automatically adjust "
        "the other dimension to maintain the original image aspect ratio.",
    )
    first_page_only = fields.Boolean()
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self._default_company_id(),
        help="Leave empty to apply to all companies. Set a specific company to "
        "restrict this image to that company only.",
    )

    def _default_company_id(self):
        return self.env.context.get("default_company_id")

    @api.constrains("pos_top", "pos_left", "width", "height")
    def _check_positive_values(self):
        """Ensure position and dimension fields have positive values."""
        for record in self:
            if record.pos_top < 0:
                raise ValidationError(_("Top position must be a positive value."))
            if record.pos_left < 0:
                raise ValidationError(_("Left position must be a positive value."))
            if record.width <= 0:
                raise ValidationError(_("Width must be greater than zero."))
            if record.height <= 0:
                raise ValidationError(_("Height must be greater than zero."))

    def _get_aspect_ratio(self):
        """Get image aspect ratio (width/height)."""
        if not self.image:
            return None
        try:
            img = Image.open(BytesIO(base64.b64decode(self.image)))
            return img.width / img.height
        except Exception:
            return None

    @api.onchange("image")
    def _onchange_image(self):
        if not self.image:
            return
        ratio = self._get_aspect_ratio()
        if not ratio:
            return
        # Set default width to 50mm and calculate height maintaining aspect ratio
        self.width = 50.0
        self.height = round(50.0 / ratio, 2)

    @api.onchange("width", "respect_image_ratio")
    def _onchange_width(self):
        if self._context.get("from_height_onchange"):
            return
        if not (self.respect_image_ratio and self.width):
            return
        ratio = self._get_aspect_ratio()
        if ratio and self.width > 0:
            # Set context flag to prevent circular onchange
            self.with_context(from_width_onchange=True).height = round(
                self.width / ratio, 2
            )

    @api.onchange("height")
    def _onchange_height(self):
        if self._context.get("from_width_onchange"):
            return
        if not (self.respect_image_ratio and self.height):
            return
        ratio = self._get_aspect_ratio()
        if ratio and self.height > 0:
            # Set context flag to prevent circular onchange
            self.with_context(from_height_onchange=True).width = round(
                self.height * ratio, 2
            )

    @api.onchange("company_id")
    def _onchange_company_id(self):
        """Prevent assigning to a different company when created from company form."""
        default_company_id = self.env.context.get("default_company_id")
        if not default_company_id:
            return
        if self.company_id and self.company_id.id != default_company_id:
            self.company_id = default_company_id
            return {
                "warning": {
                    "title": _("Company Assignment"),
                    "message": _(
                        "You cannot assign this image to a different company. "
                        "Please use the dedicated wizard to assign images to other "
                        "companies."
                    ),
                }
            }
