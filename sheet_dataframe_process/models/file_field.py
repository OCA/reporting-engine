from odoo import fields, models


class FileField(models.Model):
    _name = "file.field"
    _description = "Configuration de l'import de champ"

    config_id = fields.Many2one(
        comodel_name="file.config", required=True, ondelete="cascade"
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        ondelete="cascade",
        required=True,
        domain="[('model_id', '=', model_id)]",
        # [('model_id', '=', model_id)]
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        readonly=True,
    )
    required = fields.Boolean(
        tracking=True,
        help="Prevent to import missing data if field is missing in some records",
    )
    on_fail = fields.Selection(
        selection=[("stop", "Stop Process"), ("skip", "Skip record (TODO)")],
        default="stop",
        help="What should be the behavior in case of failure regarding constraint "
        "fields (required, format, etc)",
    )
