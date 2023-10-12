# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class IrActionReport(models.Model):

    _inherit = "ir.actions.report"

    action_report_substitution_rule_ids = fields.One2many(
        "ir.actions.report.substitution.rule",
        "action_report_id",
        string="Substitution Rules",
    )

    def _get_substitution_report(self, model, active_ids):
        self.ensure_one()
        model = self.env[model]
        for substitution_report_rule in self.action_report_substitution_rule_ids:
            domain = safe_eval(substitution_report_rule.domain)
            domain.append(("id", "in", active_ids))
            if set(model.search(domain).ids) == set(active_ids):
                return substitution_report_rule.substitution_action_report_id
        return False

    def get_substitution_report(self, active_ids):
        self.ensure_one()
        action_report = self
        substitution_report = action_report
        while substitution_report:
            action_report = substitution_report
            substitution_report = action_report._get_substitution_report(
                action_report.model, active_ids
            )
        return action_report

    @api.model
    def get_substitution_report_action(self, action, active_ids):
        if action.get("id"):
            action_report = self.browse(action["id"])
            substitution_report = action_report
            while substitution_report:
                action_report = substitution_report
                substitution_report = action_report._get_substitution_report(
                    action_report.model, active_ids
                )
            action.update(action_report.read()[0])

        return action

    def _render(self, report_ref, res_ids, data=None):
        report = self._get_report(report_ref)
        substitution_report = report.get_substitution_report(res_ids)
        return super(IrActionReport, self)._render(
            substitution_report.report_name, res_ids, data=data
        )

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report = self._get_report(report_ref)
        substitution_report = report.get_substitution_report(res_ids)
        return super(IrActionReport, self)._render_qweb_pdf(
            substitution_report, res_ids=res_ids, data=data
        )

    def report_action(self, docids, data=None, config=True):
        if docids:
            if isinstance(docids, models.Model):
                active_ids = docids.ids
            elif isinstance(docids, int):
                active_ids = [docids]
            elif isinstance(docids, list):
                active_ids = docids
            substitution_report = self.get_substitution_report(active_ids)
            return super(IrActionReport, substitution_report).report_action(
                docids, data, config
            )
        return super().report_action(docids, data, config)

    def get_action_report_substitution_rule_ids(self):
        return self.action_report_substitution_rule_ids.ids
