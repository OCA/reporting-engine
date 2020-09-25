# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ActionsReportSubstitutionRule(models.Model):

    _name = 'ir.actions.report.substitution.rule'
    _description = 'Action Report Substitution Rule'
    _order = 'sequence ASC'

    sequence = fields.Integer(default=10)
    action_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Report Action",
        required=True,
        ondelete="cascade",
    )
    model = fields.Char(related="action_report_id.model", store=True)
    domain = fields.Char(string="Domain", required=True, default="[]")
    substitution_action_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Substitution Report Action",
        required=True,
        ondelete="cascade",
        domain="[('model', '=', model)]",
    )

    @api.constrains('substitution_action_report_id', 'action_report_id')
    def _check_substitution_infinite_loop(self):
        def _check_infinite_loop(original_report, substitution_report):
            if original_report == substitution_report:
                raise ValidationError(_("Substitution infinite loop detected"))
            for (
                substitution_rule
            ) in substitution_report.action_report_substitution_rule_ids:
                _check_infinite_loop(
                    original_report,
                    substitution_rule.substitution_action_report_id,
                )

        for rec in self:
            _check_infinite_loop(
                rec.action_report_id, rec.substitution_action_report_id
            )
