# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class ReportTemplateKpiItem(models.Model):
    _name = "report.template.kpi.item"
    _description = "Report Template Kpi Item"
    _order = "sequence ASC, id ASC"

    sequence = fields.Integer(default=20)
    kind = fields.Selection(
        [("query", "Query"), ("kpi", "KPI")],
        default="query",
    )
    parent_kpi_id = fields.Many2one(
        "report.template.kpi",
        ondelete="cascade",
        required=True,
    )
    kpi_id = fields.Many2one(
        "report.template.kpi",
        ondelete="cascade",
        domain="[('template_id', '=', template_id), ('id', '!=', parent_kpi_id)]",
    )
    query_kind_id = fields.Many2one(
        "report.template.kpi.query.kind",
        domain="[('source', '=', source)]",
    )
    code = fields.Char()
    source = fields.Selection(
        selection=lambda self: self.env["report.template.kpi.query.kind"]
        ._fields["source"]
        .selection,
        compute="_compute_source",
        readonly=False,
        store=True,
    )
    domain = fields.Char(help="Domain to filter the records for this KPI item. ")
    template_id = fields.Many2one(
        related="parent_kpi_id.template_id",
    )
    positive = fields.Boolean(
        help="If checked, the KPI item will be considered positive. "
        "If not checked, it will be considered negative.",
        default=True,
    )

    @api.depends("parent_kpi_id")
    def _compute_source(self):
        for record in self:
            record.source = record.parent_kpi_id.template_id.source

    def _get_kpi_data(self, cols, kpi_data, **kwargs):
        """
        Process the KPI item and return the data for the KPI.
        This method should be overridden in subclasses if needed.
        """
        value = defaultdict(lambda: {"total": 0, "values": defaultdict(lambda: 0)})
        for item in self:
            item._get_kpi_value(cols, kpi_data, value, **kwargs)
        return value

    def _get_kpi_value(self, cols, kpi_data, value, **kwargs):
        """
        Get the value for the KPI item.
        This method should be overridden in subclasses if needed.
        """
        for col in cols:
            multiplier = 1 if self.positive else -1
            values = {}
            if self.kind == "query":
                kpi_value, values = getattr(
                    self, f"_get_kpi_value_{self.source}_{self.query_kind_id.code}"
                )(col, kpi_data, **kwargs)
            elif self.kind == "kpi":
                kpi_value = kpi_data.get(self.kpi_id.id, {}).get(col["id"], 0)["total"]
                values = (
                    kpi_data.get(self.kpi_id.id, {})
                    .get(col["id"], {})
                    .get("values", {})
                )
            for val in values:
                value[col["id"]]["values"][val] += multiplier * values[val]
            value[col["id"]]["total"] += multiplier * kpi_value
