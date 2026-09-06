# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models
from odoo.osv.expression import OR
from odoo.tools.safe_eval import safe_eval


class ReportingDummyModel(models.Model):
    _name = "reporting.dummy.model"
    _description = "Reporting Dummy Model"

    name = fields.Char()
    date = fields.Date()
    value = fields.Float()


class ReportTemplateKpiQueryKind(models.Model):
    _inherit = "report.template.kpi.query.kind"

    source = fields.Selection(
        selection_add=[("dummy", "Dummy")],
        ondelete={"dummy": "cascade"},
    )


class ReportTemplateKpiItem(models.Model):
    _inherit = "report.template.kpi.item"

    def _get_kpi_value_dummy_dummy(self, col, kpi_data, **kwargs):
        domain = [
            ("date", ">=", col["date_from"]),
            ("date", "<=", col["date_to"]),
        ]
        if self.domain:
            domain += safe_eval(self.domain)
        if domain:
            domain += domain
        if self.code:
            domain += OR(
                [[("name", "=ilike", code.strip())] for code in self.code.split(",")]
            )
        values = self.env["reporting.dummy.model"]._read_group(
            domain, groupby=("name",), aggregates=("value:sum",)
        )
        return sum(val[1] for val in values), {val[0]: val[1] for val in values}
