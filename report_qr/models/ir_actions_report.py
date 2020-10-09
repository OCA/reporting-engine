import io

import qrcode
from qrcode.image import pil, svg

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def qr_generate(self, value, box_size=3, border=5, factory="png", **kwargs):
        factories = {
            "png": pil.PilImage,
            "svg": svg.SvgImage,
            "svg-fragment": svg.SvgFragmentImage,
            "svg-path": svg.SvgPathImage,
        }
        back_color = kwargs.pop("back_color", "white")
        fill_color = kwargs.pop("fill_color", "black")
        try:
            # Defaults to png if the argument is unknown
            image_factory = factories.get(factory, pil.PilImage)
            qr = qrcode.QRCode(
                box_size=box_size, border=border, image_factory=image_factory, **kwargs
            )
            qr.add_data(value)
            qr.make()
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            arr = io.BytesIO()
            img.save(arr)
            return arr.getvalue()
        except Exception:
            raise ValueError("Cannot convert into barcode.")
