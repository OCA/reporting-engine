# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class KPIHistory(models.Model):
    """History of the KPI."""

    _name = "kpi.history"
    _description = "History of the KPI"
    _order = "date desc"

    name = fields.Char(
        size=150,
        required=True,
        default=fields.Datetime.now(),
    )
    kpi_id = fields.Many2one("kpi", "KPI", required=True)
    date = fields.Datetime(
        "Execution Date",
        required=True,
        default=lambda r: fields.Datetime.now(),
    )
    value = fields.Float(required=True)
    color = fields.Text(required=True, default="#FFFFFF")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
