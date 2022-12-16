# Copyright 2022 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models

from .outstanding_statement import OutstandingStatement


class DetailedActivityStatement(models.AbstractModel):
    """Model of Detailed Activity Statement"""

    _inherit = "report.partner_statement.activity_statement"
    _name = "report.partner_statement.detailed_activity_statement"
    _description = "Partner Detailed Activity Statement"

    def _get_account_display_prior_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        return self._get_account_display_lines2(
            company_id, partner_ids, date_start, date_end, account_type
        )

    def _get_account_display_ending_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        return self._get_account_display_lines2(
            company_id, partner_ids, date_start, date_end, account_type
        )

    def _add_currency_prior_line(self, line, currency):
        return self._add_currency_line2(line, currency)

    def _add_currency_ending_line(self, line, currency):
        return self._add_currency_line2(line, currency)


DetailedActivityStatement._get_account_display_lines2 = (
    OutstandingStatement._get_account_display_lines
)
DetailedActivityStatement._display_outstanding_lines_sql_q1 = (
    OutstandingStatement._display_outstanding_lines_sql_q1
)
DetailedActivityStatement._add_currency_line2 = OutstandingStatement._add_currency_line
