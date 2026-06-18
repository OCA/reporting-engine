# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class KPIThreshold(models.Model):
    """KPI Threshold."""

    _name = "kpi.threshold"
    _description = "KPI Threshold"

    def _compute_is_valid_threshold(self):
        for obj in self:
            # check if ranges overlap
            # TODO: This code can be done better
            obj.valid = True
            for range1 in obj.range_ids:
                if not range1.valid:
                    obj.valid = False
                    break
                for range2 in obj.range_ids - range1:
                    if (
                        range1.max_value >= range2.min_value
                        and range1.min_value <= range2.max_value
                    ):
                        obj.valid = False
                        break
            if obj.valid:
                obj.invalid_message = None
            else:
                obj.invalid_message = (
                    "Some ranges are invalid or overlapping. "
                    "Please make sure your ranges do not overlap."
                )

    name = fields.Char(required=True)
    range_ids = fields.Many2many(
        "kpi.threshold.range",
        "kpi_threshold_range_rel",
        "threshold_id",
        "range_id",
        "Ranges",
    )
    valid = fields.Boolean(
        required=True,
        compute="_compute_is_valid_threshold",
        default=True,
    )
    invalid_message = fields.Char(
        string="Message", size=100, compute="_compute_is_valid_threshold"
    )
    kpi_ids = fields.One2many("kpi", "threshold_id", "KPIs")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )

    def _range_ids_from_commands(self, commands):
        range_ids = []
        for command in commands:
            if command[0] == 6:
                range_ids = list(command[2])
            elif command[0] == 4:
                range_ids.append(command[1])
            elif command[0] == 3:
                range_ids = [
                    range_id for range_id in range_ids if range_id != command[1]
                ]
            elif command[0] == 5:
                range_ids = []
        return range_ids

    def _check_range_overlap(self, range_ids_commands):
        range_ids = self._range_ids_from_commands(range_ids_commands)
        if not range_ids:
            return
        ranges = self.env["kpi.threshold.range"].browse(range_ids)
        for range1 in ranges:
            if not range1.valid:
                continue
            for range2 in ranges - range1:
                if (
                    range2.valid
                    and range1.min_value < range2.min_value
                    and range1.max_value > range2.min_value
                ):
                    raise ValidationError(
                        self.env._(
                            "Two of your ranges are overlapping. "
                            "Make sure your ranges do not overlap!"
                        ),
                    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("range_ids"):
                self._check_range_overlap(vals["range_ids"])
        return super().create(vals_list)

    def get_color(self, kpi_value):
        color = "#FFFFFF"
        for obj in self:
            for range_obj in obj.range_ids:
                if (
                    range_obj.min_value <= kpi_value <= range_obj.max_value
                    and range_obj.valid
                ):
                    color = range_obj.color
        return color
