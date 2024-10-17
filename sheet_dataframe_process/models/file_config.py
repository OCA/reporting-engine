from odoo import Command, fields, models


class FileConfig(models.Model):
    _name = "file.config"
    _inherit = "mail.thread"
    _description = "File Configuration"
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
    partner_ids = fields.Many2many(
        comodel_name="res.partner", domain="[('active', 'in', (True, False))]"
    )
    field_ids = fields.One2many(
        comodel_name="file.field", inverse_name="config_id", copy=True
    )
    field_match_ids = fields.One2many(
        comodel_name="file.partner.field", inverse_name="config_id", copy=True
    )

    def populate_match_lines(self):
        # TODO use api depends instead of ui button
        self.ensure_one()
        for partner in self.partner_ids:
            fields_ = self.field_match_ids.filtered(
                lambda s: s.partner_id == partner
            ).mapped("field_id")
            line_ids = self.field_ids.filtered(
                lambda s: s.field_id not in fields_
            ).mapped("id")
            self.field_match_ids = [
                Command.create({"partner_id": partner.id, "line_id": x})
                for x in line_ids
            ]
        self.field_match_ids.filtered(
            lambda s: s.partner_id not in s.config_id.partner_ids
        ).unlink()

    def _refresh_conf_hook(self):
        "You use it to trigger specific behavior"
