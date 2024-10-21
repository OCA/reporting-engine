from odoo import Command, fields, models

# Demo record
UISTRING = "sheet_dataframe_process.file_config_contact"


class FileConfig(models.Model):
    _name = "file.config"
    _inherit = "mail.thread"
    _description = "File Configuration"
    _rec_name = "model_id"

    model_id = fields.Many2one(
        comodel_name="ir.model",
        required=True,
        copy=False,
        ondelete="cascade",
        tracking=True,
    )
    code = fields.Char(help="Allow to browse between several identical models")
    action = fields.Selection(
        selection=[
            ("display", "Display"),
            ("dataframe", "Dataframe"),
        ],
        default="display",
        tracking=True,
        help="Some other behaviors can be implemented",
    )
    on_fail = fields.Selection(
        selection=[("stop", "Stop"), ("skip", "Skip record (TODO)")],
        default="stop",
        tracking=True,
        help="What should be the behavior in case of failure regarding constraint "
        "fields (required, format, etc)\n\n"
        " - Stop: stop the process by raising an exception\n"
        " - Skip record: current line'll be ignored from the next process",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        domain="[('active', 'in', (True, False))]",
        tracking=True,
    )
    field_ids = fields.One2many(
        comodel_name="file.field", inverse_name="config_id", copy=True
    )
    field_match_ids = fields.One2many(
        comodel_name="file.partner.field", inverse_name="config_id", copy=True
    )

    def populate_match_lines(self):
        # TODO use api depends instead of ui button ?
        self.ensure_one()
        for partner in self.partner_ids:
            ffields = self.field_match_ids.filtered(
                lambda s, partner=partner: s.partner_id == partner
            ).mapped("field_id")
            line_ids = self.field_ids.filtered(
                lambda s, ffields=ffields: s.field_id not in ffields
            ).mapped("id")
            self.field_match_ids = [
                Command.create({"partner_id": partner.id, "line_id": x})
                for x in line_ids
            ]
        self.field_match_ids.filtered(
            lambda s: s.partner_id not in s.config_id.partner_ids
        ).unlink()
        for rec in self:
            if rec == self.env.ref(UISTRING):
                rec._populate_demo_column_names()

    def _populate_match(self, mfield, mstring, uidstring):
        record = self.field_match_ids.filtered(
            lambda s, field=mfield, uidstring=uidstring: s.field_id.name == field
            and s.partner_id == s.config_id.partner_ids[0]
        )
        if record:
            record.matching_column = mstring

    def _populate_demo_column_names(self):
        self.field_match_ids.matching_column = False
        self._populate_match("street", "myStreet", UISTRING)
        self._populate_match("street2", "Second street", UISTRING)
        self._populate_match("country_code", "Country", UISTRING)
