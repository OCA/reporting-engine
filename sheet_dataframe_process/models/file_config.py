from odoo import fields, models


class FileConfig(models.Model):
    _name = "file.config"
    _inherit = "mail.thread"
    _description = "Config import fournisseur"
    _rec_name = "model_id"

    model_id = fields.Many2one(
        comodel_name="ir.model", required=True, ondelete="cascade"
    )
    code = fields.Char(help="Allow to browse between several identical models")
    action = fields.Selection(
        selection=[
            ("display", "Display"),
            ("dataframe", "Dataframe"),
        ],
        default="display",
        help="Some other behaviors can be implemented",
    )
    partner_ids = fields.Many2many(comodel_name="res.partner")
    field_ids = fields.One2many(comodel_name="file.field", inverse_name="config_id")
    field_match_ids = fields.One2many(
        comodel_name="file.partner.field", inverse_name="config_id"
    )

    def populate_match_lines(self):
        self.ensure_one()
        return NotImplemented
