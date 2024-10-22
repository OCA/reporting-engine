from odoo import fields, models


class FileField(models.Model):
    _name = "file.field"
    _inherit = ["mail.thread"]
    _description = "Configuration de l'import de champ"
    _order = "field_id ASC"

    config_id = fields.Many2one(
        comodel_name="file.config", required=True, ondelete="cascade"
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        ondelete="cascade",
        required=True,
        domain="[('model_id', '=', model_id)]",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        related="config_id.model_id",
        readonly=True,
    )
    required = fields.Boolean(
        help="Prevent to import missing data if field is missing in some records",
    )
    check_type = fields.Boolean(
        help="Check data type is compatible",
    )
