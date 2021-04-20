from odoo import fields, models


class ReportPaperformatLabel(models.Model):
    _name = "report.paperformat.label"
    _inherits = {"report.paperformat": "paperformat_id"}
    _description = "Label Paper Format"

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
    label_padding_top = fields.Float("Label Padding Top (mm)", default=2)
    label_padding_right = fields.Float("Label Padding Right (mm)", default=2)
    label_padding_bottom = fields.Float("Label Padding Bottom (mm)", default=2)
    label_padding_left = fields.Float("Label Padding Left (mm)", default=2)
    label_margin_top = fields.Float("Label Margin Top (mm)", default=2)
    label_margin_right = fields.Float("Label Margin Right (mm)", default=2)
    label_margin_bottom = fields.Float("Label Margin Bottom (mm)", default=2)
    label_margin_left = fields.Float("Label Margin Left (mm)", default=2)

    # Overload inherits defaults
    orientation = fields.Selection(inherited=True, default="Portrait")
    header_spacing = fields.Integer(inherited=True, default=0)
    margin_top = fields.Float(inherited=True, default=7)
    margin_bottom = fields.Float(inherited=True, default=7)
