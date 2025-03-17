# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class KPIThreshold(models.Model):
    """KPI Threshold."""

    _name = "kpi.threshold"
    _description = "KPI Threshold"

    name = fields.Char(required=True)
    range_ids = fields.Many2many(
        "kpi.threshold.range",
        "kpi_threshold_range_rel",
        "threshold_id",
        "range_id",
        "Ranges",
    )
    kpi_ids = fields.One2many("kpi", "threshold_id", "KPIs")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )

    def _check_overlap(self):
        # check if ranges overlap
        # TODO: This code can be improved
        for record in self:
            if record.range_ids:
                for range1 in record.range_ids:
                    for range2 in record.range_ids:
                        if (
                            range1.max_value > range2.min_value
                            and range1.min_value < range2.min_value
                        ):
                            raise ValidationError(
                                _(
                                    "Two of your ranges are overlapping. "
                                    "Make sure your ranges do not overlap!"
                                ),
                            )

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
