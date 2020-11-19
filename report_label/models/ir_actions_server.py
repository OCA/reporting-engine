from odoo import api, models, fields


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    state = fields.Selection(
        selection_add=[("report_label", "Print self-adhesive labels")]
    )
    label_template = fields.Char(
        "Label QWeb Template",
        help="The QWeb template key to render the labels",
        states={
            "report_label": [("required", True)]
        }
    )
    label_paperformat_id = fields.Many2one(
        "report.paperformat.label",
        "Label Paper Format",
        states={
            "report_label": [("required", True)]
        }
    )

    @api.multi
    def report_label_associated_view(self):
        """ View the associated qweb templates """
        self.ensure_one()
        action = self.env.ref('base.action_ui_view', raise_if_not_found=False)
        if not action or len(self.label_template.split('.')) < 2:
            return False
        res = action.read()[0]
        res['domain'] = [
            ('type', '=', 'qweb'),
            '|',
            ('name', 'ilike', self.label_template.split('.')[1]),
            ('key', '=', self.label_template),
        ]
        return res

    @api.model
    def run_action_report_label_multi(self, action, eval_context=None):
        """ Show report label wizard """
        context = dict(self.env.context)
        context.update({
            "label_template": action.label_template,
            "label_paperformat_id": action.label_paperformat_id.id,
            "res_model_id": action.model_id.id,
        })
        return {
            "name": action.name,
            "type": "ir.actions.act_window",
            "res_model": "report.label.wizard",
            "context": str(context),
            "view_mode": "form",
            "target": "new",
        }
