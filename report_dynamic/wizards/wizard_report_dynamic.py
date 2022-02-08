from odoo import _, fields, models


class WizardReportDynamic(models.TransientModel):
    _name = "wizard.report.dynamic"
    _description = "Select template for report for record(s)"

    template_id = fields.Many2one(
        "report.dynamic",
        domain=lambda self: [
            ("is_template", "=", True),
            ("model_id.model", "=", self.env.context.get("active_model")),
        ],
    )
    model_name = fields.Char(related="template_id.model_name")

    def action_generate_reports(self):
        active_model = self.env.context.get("active_model")
        active_ids = self.env.context.get("active_ids")
        records = self.env[active_model].browse(active_ids)
        reports = self.env["report.dynamic"]
        for record in records:
            if record._name != self.template_id.model_model:
                continue
            # check that the record has a name field
            if hasattr(record, "name"):
                record_name = record.name
            else:
                record_name = _("Model {}, id {}").format(record._name, record.id)
            report = self.template_id.copy(
                {
                    "is_template": False,
                    "name": record_name,
                    "res_id": record.id,
                    "template_id": self.template_id.id,
                }
            )
            reports += report
        return {
            "name": "Generated Reports",
            "type": "ir.actions.act_window",
            "res_model": "report.dynamic",
            "domain": [("id", "in", reports.ids)],
            "view_mode": "tree,form",
            "target": "current",
        }
