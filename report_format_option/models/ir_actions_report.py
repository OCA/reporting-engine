# Copyright 2024 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class IrActionReport(models.Model):
    _inherit = "ir.actions.report"

    encoding = fields.Char(
        help="Encoding to be applied to the generated CSV file. " "e.g. cp932"
    )
    encode_error_handling = fields.Selection(
        selection=[("ignore", "Ignore"), ("replace", "Replace")],
        help="If nothing is selected, CSV export will fail with an error message when "
        "there is a character that fail to be encoded.",
    )
    show_encoding = fields.Boolean(compute="_compute_show_encoding")
    line_ending = fields.Char(
        help="Line ending to be applied to the generated report. e.g., crlf"
    )

    def _compute_show_encoding(self):
        for report in self:
            report.show_encoding = False
