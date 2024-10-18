from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def sheet_dataframe_import(self):
        self.ensure_one()
        transient = self.env["sheet.dataframe.transient"].create(
            {
                "config_id": self.env.context.get("config_id")["id"],
                "partner_id": self.id,
            }
        )
        action = self.env.ref(
            "sheet_dataframe_process.sheet_dataframe_transient_action"
        )._get_action_dict()
        action["res_id"] = transient.id
        return action
