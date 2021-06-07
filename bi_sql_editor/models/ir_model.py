from odoo import models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    def _add_manual_fields(self, model):
        super()._add_manual_fields(model)
        self.env["bi.sql.view"].check_manual_fields(model)
