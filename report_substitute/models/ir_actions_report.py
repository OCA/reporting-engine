# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval


class IrActionReport(models.Model):

    _inherit = 'ir.actions.report'

    action_report_substitution_criteria_ids = fields.One2many(
        comodel_name="ir.actions.report.substitution.criteria",
        inverse_name="action_report_id",
        string="Substitution Criteria",
    )

    @api.multi
    def _get_substitution_report(self, model, active_ids):
        self.ensure_one()
        model = self.env[model]
        for (
            substitution_report_criteria
        ) in self.action_report_substitution_criteria_ids:
            domain = safe_eval(substitution_report_criteria.domain)
            domain.append(('id', 'in', active_ids))
            if set(model.search(domain).ids) == set(active_ids):
                return (
                    substitution_report_criteria.substitution_action_report_id
                )
        return False

    @api.multi
    def render(self, res_ids, data=None):
        substitution_report = self._get_substitution_report(
            self.model, res_ids
        )
        if substitution_report:
            return substitution_report.render(res_ids)
        return super().render(res_ids, data)
