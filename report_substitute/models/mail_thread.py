# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MailThread(models.AbstractModel):

    _inherit = 'mail.thread'

    @api.multi
    def message_post_with_template(self, template_id, **kwargs):
        template = self.env['mail.template'].browse(template_id)
        old_report = False
        if template and template.report_template and self.ids:
            active_ids = self.ids
            old_report = template.report_template
            template.report_template = old_report.get_substitution_report(
                active_ids
            )
        res = super().message_post_with_template(template_id, **kwargs)
        if old_report:
            template.report_template = old_report
        return res
