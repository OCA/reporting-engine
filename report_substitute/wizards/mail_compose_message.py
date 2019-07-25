# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailComposeMessage(models.TransientModel):

    _inherit = 'mail.compose.message'

    @api.multi
    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        old_report_template = False
        if (
            self.template_id
            and self.template_id.report_template
            and self.env.context.get('active_ids')
        ):
            active_ids = self.env.context.get('active_ids')
            old_report_template = self.template_id.report_template
            self.template_id.report_template = (
                old_report_template.get_substitution_report(active_ids)
            )
        res = super().onchange_template_id_wrapper()
        if old_report_template:
            self.template_id.report_template = old_report_template
        return res
