# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BiSQLView(models.Model):
    _name = "bi.sql.view"
    _inherit = ["bi.sql.view"]

    server_action_ids = fields.Many2many(
        comodel_name="ir.actions.server",
        readonly=True,
        states={"model_valid": [("readonly", False)]},
    )

    def unlink(self):
        if self.mapped("server_action_ids"):
            self.mapped("server_action_ids").unlink()
        return super(BiSQLView, self).unlink()

    def button_create_sql_view_and_model(self):
        res = super(BiSQLView, self).button_create_sql_view_and_model()
        for sql_view in self:
            sql_view.server_action_ids.write({"model_id": sql_view.model_id.id})
        return res

    def button_set_draft(self):
        self.mapped("server_action_ids").unlink_action()
        # Avoid the on cascade delete
        self.mapped("server_action_ids").write({"model_id": False})
        return super(BiSQLView, self).button_set_draft()

    def button_create_ui(self):
        self.server_action_ids.create_action()
        return super(BiSQLView, self).button_create_ui()
