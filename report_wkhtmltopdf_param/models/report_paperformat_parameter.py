# Copyright 2017 Avoin.Systems
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReportPaperformatParameter(models.Model):
    _name = "report.paperformat.parameter"
    _description = "wkhtmltopdf parameters"

    paperformat_id = fields.Many2one(
        "report.paperformat",
        "Paper Format",
        required=True,
    )

    name = fields.Char(
        required=True,
        help="The command argument name. Remember to add prefix -- or -",
    )

    value = fields.Char()
