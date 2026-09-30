# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging
from ast import literal_eval
from io import BytesIO

from PIL import Image

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain

_logger = logging.getLogger(__name__)


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
    report_ids = fields.Many2many(
        comodel_name="ir.actions.report",
        relation="ir_actions_report_positioned_image_rel",
        column1="image_id",
        column2="report_id",
        string="Reports",
        help="Reports this image is placed on. The condition is validated "
        "against the models they render.",
    )
    domain = fields.Char(
        string="Condition",
        help="Leave empty to print this image on every page of every record. "
        "When set, the image is printed only on the records matching it. The "
        "domain is evaluated against whichever model the printed report "
        "renders, so one image can guard several reports as long as they share "
        "the field paths it uses. "
        "Example: [('partner_id.country_id.code', '=', 'JP')]",
    )

    def _default_company_id(self):
        return self.env.context.get("default_company_id")

    @api.constrains("pos_top", "pos_left", "width", "height")
    def _check_positive_values(self):
        """Ensure position and dimension fields have positive values."""
        for record in self:
            if record.pos_top < 0:
                raise ValidationError(
                    self.env._("Top position must be a positive value.")
                )
            if record.pos_left < 0:
                raise ValidationError(
                    self.env._("Left position must be a positive value.")
                )
            if record.width <= 0:
                raise ValidationError(self.env._("Width must be greater than zero."))
            if record.height <= 0:
                raise ValidationError(self.env._("Height must be greater than zero."))

    @api.constrains("domain", "report_ids")
    def _check_domain(self):
        """Reject a condition that a report using this image cannot evaluate.

        The condition carries no model of its own: it is evaluated at print
        time against whatever the printed report renders. Checking it against
        every linked report's model turns a typo into a write-time error
        instead of an image that silently drops out of a print run.
        """
        for record in self.filtered("domain"):
            for model_name in set(record.report_ids.mapped("model")):
                if model_name and model_name in self.env:
                    record._validate_domain(self.env[model_name])

    def _validate_domain(self, model):
        """Raise unless this image's condition is valid for ``model``."""
        self.ensure_one()
        try:
            Domain(literal_eval(self.domain)).validate(model)
        except Exception as e:
            raise ValidationError(
                self.env._(
                    "The condition of %(image)s cannot be evaluated on "
                    "%(model)s: %(error)s",
                    image=self.name,
                    model=model._name,
                    error=e,
                )
            ) from e

    def _get_condition_matched_ids(self, model, res_ids):
        """Return the subset of ``res_ids`` matching this image's condition.

        A condition that does not fit ``model`` matches nothing rather than
        everything: an image is printed only where it was meant to be. Run as
        sudo so that the output does not depend on the record rules of the user
        requesting the report.
        """
        self.ensure_one()
        try:
            domain = Domain(literal_eval(self.domain))
            domain.validate(model)
        except Exception:
            _logger.warning(
                "Skipping positioned image %s: its condition %r cannot be "
                "evaluated on %s.",
                self.display_name,
                self.domain,
                model._name,
            )
            return set()
        return set(model.sudo().search(Domain("id", "in", res_ids) & domain).ids)

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
        if self.env.context.get("from_height_onchange"):
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
        if self.env.context.get("from_width_onchange"):
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
                    "title": self.env._("Company Assignment"),
                    "message": self.env._(
                        "You cannot assign this image to a different company. "
                        "Please use the dedicated wizard to assign images to other "
                        "companies."
                    ),
                }
            }
