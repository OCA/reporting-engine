from odoo import models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        dnf_models = set(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("report.display_name_in_footer_models", default="")
            .replace(" ", "")
            .split(",")
        )
        report_model = self._get_report(report_ref).model
        if (
            report_model in dnf_models or "all" in dnf_models
        ) and f"-{report_model}" not in dnf_models:
            data = data and dict(data) or {}
            data.update({"display_name_in_footer": True})
        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
