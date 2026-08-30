from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def get_paperformat(self):
        # Allow to define paperformat via context
        res = super().get_paperformat()
        if self.env.context.get("paperformat_id"):
            res = self.env["report.paperformat"].browse(
                self.env.context.get("paperformat_id")
            )
        return res
