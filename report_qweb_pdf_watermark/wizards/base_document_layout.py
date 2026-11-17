from odoo import fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    pdf_watermark = fields.Binary(
        "Watermark", related="company_id.pdf_watermark", readonly=False
    )
