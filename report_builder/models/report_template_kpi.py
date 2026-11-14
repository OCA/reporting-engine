# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReportTemplateKpi(models.Model):
    _name = "report.template.kpi"
    _description = "KPI"
    _order = "template_id, sequence ASC, name"

    sequence = fields.Integer(default=10)
    template_id = fields.Many2one("report.template", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    code = fields.Char(
        compute="_compute_code",
        store=True,
        readonly=False,
    )
    invisible = fields.Boolean(default=False)
    item_ids = fields.One2many(
        "report.template.kpi.item",
        "parent_kpi_id",
    )
    mis_builder_formula = fields.Char(
        compute="_compute_mis_builder_formula",
        help="Formula for MIS Builder",
    )
    style_id = fields.Many2one("report.style")
    is_currency = fields.Boolean(default=True)

    @api.depends(
        "item_ids",
        "item_ids.code",
        "item_ids.positive",
        "item_ids.domain",
        "item_ids.code",
        "item_ids.kpi_id",
    )
    def _compute_mis_builder_formula(self):
        for record in self:
            record.mis_builder_formula = record._get_mis_builder_formula()

    def _get_mis_builder_formula(self):
        """
        Generate the MIS Builder formula based on the items.
        This method should be overridden in subclasses if needed.
        """
        formula_parts = []
        for item in self.item_ids:
            if item.kind == "query":
                part = f"{item.query_kind_id.code}[{item.code}]"
                if item.domain:
                    part = f"{part}{item.domain}"
            elif item.kind == "kpi":
                part = f"{item.kpi_id.code}"
            else:
                continue
            if not item.positive:
                part = f"-{part}"
            else:
                part = f"+{part}" if formula_parts else part
            formula_parts.append(part)
        return "".join(formula_parts)

    @api.depends("name")
    def _compute_code(self):
        for record in self:
            record.code = (record.name or " ").replace(" ", "_").lower()

    def _process_information(self, cols, kpi_data, **kwargs):
        unprocessed_items = self.browse()
        for kpi in self:
            if not kpi._process_item(cols, kpi_data, **kwargs):
                unprocessed_items |= kpi
        if len(unprocessed_items) == len(self):
            raise ValidationError(_("KPIs cannot be processed"))
        if unprocessed_items:
            unprocessed_items._process_information(cols, kpi_data, **kwargs)

    def _process_item(self, cols, kpi_data, **kwargs):
        if any(
            item.kpi_id.id not in kpi_data
            for item in self.item_ids
            if item.kind == "kpi"
        ):
            return False
        kpi_data[self.id] = self.item_ids._get_kpi_data(cols, kpi_data, **kwargs)
        return True
