# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailComposeMessage(models.TransientModel):

    _inherit = "mail.compose.message"

    @api.onchange("template_id")
    def _onchange_template_id_wrapper(self):
        if self.template_id:
            report_template = self.template_id.report_template
            active_ids = []
            if self.env.context.get("active_ids"):
                active_ids = self.env.context.get("active_ids")
            elif self.env.context.get("default_res_id"):
                active_ids = [self.env.context.get("default_res_id")]
            if (
                report_template
                and report_template.action_report_substitution_rule_ids
                and active_ids
            ):
                old_tmpl = report_template
                self.template_id.report_template = old_tmpl.get_substitution_report(
                    active_ids
                )
                onchange_result_with_substituted_report = (
                    super()._onchange_template_id_wrapper()
                )
                self.template_id.report_template = old_tmpl
                return onchange_result_with_substituted_report
        return super()._onchange_template_id_wrapper()
