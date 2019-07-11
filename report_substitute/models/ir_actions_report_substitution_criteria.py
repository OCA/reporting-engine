# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ActionsReportSubstitutionCriteria(models.Model):

    _name = 'ir.actions.report.substitution.criteria'
    _description = 'Action Report Substitution Criteria'
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
        domain="[('model', '=', model)]"
    )
