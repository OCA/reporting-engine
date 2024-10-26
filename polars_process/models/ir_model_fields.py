from odoo import api, models


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    @api.depends("field_description", "model")
    def _compute_display_name(self):
        super()._compute_display_name()
        if self.env.context.get("technical_name"):
            for field in self:
                if self.env.context.get("technical_name"):
                    field.display_name = field.name
        return
