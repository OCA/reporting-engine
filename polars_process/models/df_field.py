from odoo import fields, models


class FileField(models.Model):
    _name = "df.field"
    _inherit = ["mail.thread"]
    _description = "Configuration de l'import de champ"
    _order = "field_id ASC"

    dataframe_id = fields.Many2one(
        comodel_name="dataframe", required=True, ondelete="cascade"
    )
    sequence = fields.Integer()
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        ondelete="cascade",
        required=True,
        domain="[('model_id', '=', model_id)]",
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        related="dataframe_id.model_id",
        readonly=True,
    )
    name = fields.Char(help="Name field in the source file (spreadsheet)")
    renamed = fields.Char(help="If specified, renamed in dataframe")
    required = fields.Boolean(
        help="Prevent to import missing data if field is missing in some records",
    )
    check_type = fields.Boolean(
        help="Check data type is compatible",
    )
