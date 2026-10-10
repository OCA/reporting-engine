# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReportTemplateKpiQueryKind(models.Model):
    """
    This model should be filled only with master data, not by the user itself
    """

    _name = "report.template.kpi.query.kind"
    _description = "KPI Query Kind"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    source = fields.Selection(
        selection=[],
        required=True,
    )
