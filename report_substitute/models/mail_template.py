# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import pycompat


class MailTemplate(models.Model):

    _inherit = 'mail.template'

    @api.multi
    def generate_email(self, res_ids, fields=None):
        old_report = False
        active_ids = res_ids
        if self.report_template and res_ids:
            if isinstance(active_ids, pycompat.integer_types):
                active_ids = [active_ids]
            old_report = self.report_template
            self.report_template = old_report.get_substitution_report(
                active_ids
            )
        res = super().generate_email(res_ids, fields)
        if old_report:
            self.report_template = old_report
        return res
