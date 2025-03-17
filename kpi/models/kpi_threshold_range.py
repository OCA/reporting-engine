# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


def is_one_value(result):
    # check if sql query returns only one value
    if type(result) is dict and "value" in result.dictfetchone():
        return True
    elif type(result) is list and "value" in result[0]:
        return True
    else:
        return False


RE_SELECT_QUERY = re.compile(
    ".*("
    + "|".join(
        (
            "INSERT",
            "UPDATE",
            "DELETE",
            "CREATE",
            "ALTER",
            "DROP",
            "GRANT",
            "REVOKE",
            "INDEX",
        )
    )
    + ")"
)


def is_sql_or_ddl_statement(query):
    """Check if sql query is a SELECT statement"""
    return not RE_SELECT_QUERY.match(query.upper())


class KPIThresholdRange(models.Model):
    """
    KPI Threshold Range
    """

    _name = "kpi.threshold.range"
    _description = "KPI Threshold Range"

    @api.model
    def _selection_value_type(self):
        return [
            ("static", "Fixed value"),
            ("python", "Python Code"),
            ("local", "SQL - Local DB"),
        ]

    name = fields.Char(required=True)
    min_type = fields.Selection(
        selection="_selection_value_type", required=True, default="static"
    )
    min_value = fields.Float(string="Minimum Value", compute="_compute_range")
    min_fixed_value = fields.Float("Minimum Fixed Value")
    min_code = fields.Text("Minimum Computation Code")
    max_type = fields.Selection(
        selection="_selection_value_type", required=True, default="static"
    )
    max_value = fields.Float(string="Maximum Value", compute="_compute_range")
    max_fixed_value = fields.Float("Maximum Fixed Value")
    max_code = fields.Text("Maximum Computation Code")
    error = fields.Char("Maximum Error", compute="_compute_range")
    color = fields.Char(help="Choose your color")
    threshold_ids = fields.Many2many(
        "kpi.threshold",
        "kpi_threshold_range_rel",
        "range_id",
        "threshold_id",
        "Thresholds",
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )

    def _compute_range(self):
        for record in self:
            min_value = max_value = None
            error = ""
            try:
                if record.min_type == "local" and is_sql_or_ddl_statement(
                    record.min_code
                ):
                    self.env.cr.execute(record.min_code)
                    dic = self.env.cr.dictfetchall()
                    if is_one_value(dic):
                        min_value = dic[0]["value"]
                elif record.min_type == "python":
                    min_value = safe_eval(record.min_code)
                else:
                    min_value = record.min_fixed_value
                if record.max_type == "local" and is_sql_or_ddl_statement(
                    record.max_code
                ):
                    self.env.cr.execute(record.max_code)
                    dic = self.env.cr.dictfetchall()
                    if is_one_value(dic):
                        max_value = dic[0]["value"]
                elif record.min_type == "python":
                    max_value = safe_eval(record.max_code)
                else:
                    max_value = record.max_fixed_value
            except Exception as e:
                min_value = max_value = None
                error = str(e)
            record.min_value = min_value
            record.max_value = max_value
            record.error = error
            record._check_valid_range()

    def _check_valid_range(self):
        for record in self:
            if record.max_value < record.min_value:
                raise ValidationError(
                    _(
                        "Minimum value is greater than the maximum value. "
                        "Please adjust them."
                    )
                )
            for threshold in record.threshold_ids:
                threshold._check_overlap()
