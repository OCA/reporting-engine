# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class ReportInstanceColumn(models.Model):
    _name = "report.instance.column"
    _description = "Report Instance Column"  # TODO

    name = fields.Char(required=True)
    instance_id = fields.Many2one("report.instance", required=True)
    mode = fields.Selection(
        [
            ("date", "Fixed Date"),
            ("relative", "Relative to Base Date"),
        ],
        default="relative",
    )
    date_from = fields.Date()
    date_to = fields.Date()
    date_type = fields.Selection(
        [
            ("days", "Day"),
            ("weeks", "Week"),
            ("months", "Month"),
            ("years", "Year"),
        ],
        default="months",
        string="Period type",
    )
    duration_type = fields.Selection(
        [
            ("days", "Day"),
            ("weeks", "Week"),
            ("months", "Month"),
            ("years", "Year"),
        ],
        default="months",
    )
    is_ytd = fields.Boolean(
        default=False,
        string="Year to date",
        help="Forces the start date to Jan 1st of the relevant year",
    )
    offset = fields.Integer(help="Offset from current period", default=-1)
    duration = fields.Integer(help="Number of periods", default=1)
    compute_date_from = fields.Date(
        compute="_compute_compute_date",
    )
    compute_date_to = fields.Date(
        compute="_compute_compute_date",
    )
    sequence = fields.Integer(
        default=10,
    )

    @api.depends(
        "instance_id.base_date",
        "date_type",
        "date_from",
        "date_to",
        "mode",
        "is_ytd",
        "offset",
        "duration",
        "duration_type",
    )
    def _compute_compute_date(self):
        for record in self:
            record.compute_date_from, record.compute_date_to = (
                record._get_compute_date()
            )

    def _get_compute_date(self, pivot_date=None):
        if self.mode == "date":
            return self.date_from, self.date_to
        elif self.mode == "relative":
            compute_date_from = (
                pivot_date or self.instance_id.base_date or fields.Date.today()
            ) + relativedelta(**{self.date_type: self.offset})
            compute_date_to = compute_date_from + relativedelta(
                **{self.duration_type: self.duration}
            )
            if self.is_ytd:
                compute_date_from = compute_date_from.replace(month=1, day=1)
            return compute_date_from, compute_date_to

    def _get_data(self, pivot_date=None):
        columns = []
        for column in self:
            date_from, date_to = column._get_compute_date(pivot_date)
            columns.append(
                {
                    "id": column.id,
                    "name": column.name,
                    "mode": column.mode,
                    "date_from": fields.Date.to_string(date_from),
                    "date_to": fields.Date.to_string(date_to),
                }
            )
        return columns
