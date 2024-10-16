from odoo import fields, models


class FilePartnerField(models.Model):
    _name = "file.partner.field"
    _inherits = {"file.field": "line_id"}
    _description = "Configuration de l'import de champ"

    line_id = fields.Many2one(
        comodel_name="file.field", required=True, ondelete="cascade"
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        readonly=True,
    )
    matching_column = fields.Char(help="Field name in spreadsheet")
