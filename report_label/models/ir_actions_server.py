# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    state = fields.Selection(
        selection_add=[("report_label", "Print self-adhesive labels")],
        ondelete={"report_label": "cascade"},
    )
    label_template = fields.Char(
        "Label QWeb Template",
        help="The QWeb template key to render the labels",
        states={"report_label": [("required", True)]},
    )
    label_paperformat_id = fields.Many2one(
        "report.paperformat.label",
        "Label Paper Format",
        states={"report_label": [("required", True)]},
    )

    def report_label_associated_view(self):
        """View the associated qweb templates"""
        self.ensure_one()
        action = self.env.ref("base.action_ui_view", raise_if_not_found=False)
        if not action or len(self.label_template.split(".")) < 2:
            return False
        res = action.read()[0]
        res["domain"] = [
            ("type", "=", "qweb"),
            "|",
            ("name", "ilike", self.label_template.split(".")[1]),
            ("key", "=", self.label_template),
        ]
        return res

    def _run_action_report_label_multi(self, eval_context=None):
        """Show report label wizard"""
        context = dict(self.env.context)
        context.update(
            {
                "label_template": self.label_template,
                "label_paperformat_id": self.label_paperformat_id.id,
                "res_model_id": self.model_id.id,
            }
        )
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "report.label.wizard",
            "context": context,
            "view_mode": "form",
            "target": "new",
        }
