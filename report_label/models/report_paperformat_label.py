from odoo import fields, models


class ReportPaperformatLabel(models.Model):
    _name = "report.paperformat.label"
    _description = "Label Paper Format"

    name = fields.Char(required=True)

    paperformat_id = fields.Many2one(
        "report.paperformat",
        string="Paper Format",
        required=True,
        ondelete="cascade",
    )
    label_width = fields.Float(
        "Label Width (mm)",
        default=60,
        required=True,
    )
    label_height = fields.Float(
        "Label Height (mm)",
        default=42.3,
        required=True,
    )
    label_background_color = fields.Char(default="#FFFFFF")
    label_padding_top = fields.Float("Label Padding Top (mm)", default=2)
    label_padding_right = fields.Float("Label Padding Right (mm)", default=2)
    label_padding_bottom = fields.Float("Label Padding Bottom (mm)", default=2)
    label_padding_left = fields.Float("Label Padding Left (mm)", default=2)
    label_margin_top = fields.Float("Label Margin Top (mm)", default=2)
    label_margin_right = fields.Float("Label Margin Right (mm)", default=2)
    label_margin_bottom = fields.Float("Label Margin Bottom (mm)", default=2)
    label_margin_left = fields.Float("Label Margin Left (mm)", default=2)
