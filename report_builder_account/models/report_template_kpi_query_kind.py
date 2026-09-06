# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReportTemplateKpiQueryKind(models.Model):
    _inherit = "report.template.kpi.query.kind"

    source = fields.Selection(
        selection_add=[("account", "Account")],
        ondelete={"account": "cascade"},
    )
