# Copyright 2018 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.tools.float_utils import float_is_zero


class OutstandingStatement(models.AbstractModel):
    """Model of Outstanding Statement"""

    _inherit = "statement.common"
    _name = "report.partner_statement.outstanding_statement"
    _description = "Partner Outstanding Statement"

    def _display_outstanding_lines_sql_q1(self, partners, date_end, account_type):
        partners = tuple(partners)
        return str(
            self._cr.mogrify(
                """
            SELECT l.id, m.name AS move_id, l.partner_id, l.date, l.name,
                l.blocked, l.currency_id, l.company_id,
            CASE WHEN l.ref IS NOT NULL
                THEN l.ref
                ELSE m.ref
            END as ref,
            CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                THEN avg(l.amount_currency)
                ELSE avg(l.debit)
            END as debit,
            CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                THEN avg(l.amount_currency * (-1))
                ELSE avg(l.credit)
            END as credit,
            CASE WHEN l.balance > 0.0
                THEN l.balance - sum(coalesce(pd.amount, 0.0))
                ELSE l.balance + sum(coalesce(pc.amount, 0.0))
            END AS open_amount,
            CASE WHEN l.balance > 0.0
                THEN l.amount_currency - sum(coalesce(pd.debit_amount_currency, 0.0))
                ELSE l.amount_currency + sum(coalesce(pc.credit_amount_currency, 0.0))
            END AS open_amount_currency,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM account_move_line l
            JOIN account_account aa ON (aa.id = l.account_id)
            JOIN account_move m ON (l.move_id = m.id)
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.credit_move_id = l2.id
                WHERE l2.date <= %(date_end)s
            ) as pd ON pd.debit_move_id = l.id
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.debit_move_id = l2.id
                WHERE l2.date <= %(date_end)s
            ) as pc ON pc.credit_move_id = l.id
            WHERE l.partner_id IN %(partners)s
                AND (
                    (pd.id IS NOT NULL AND
                        pd.max_date <= %(date_end)s) OR
                    (pc.id IS NOT NULL AND
                        pc.max_date <= %(date_end)s) OR
                    (pd.id IS NULL AND pc.id IS NULL)
                ) AND l.date <= %(date_end)s AND m.state IN ('posted')
                AND aa.account_type = %(account_type)s
            GROUP BY l.id, l.partner_id, m.name, l.date, l.date_maturity, l.name,
                CASE WHEN l.ref IS NOT NULL
                    THEN l.ref
                    ELSE m.ref
                END,
                l.blocked, l.currency_id, l.balance, l.amount_currency, l.company_id
            """,
                locals(),
            ),
            "utf-8",
        )

    def _display_outstanding_lines_sql_q2(self, sub):
        return str(
            self._cr.mogrify(
                f"""
                SELECT {sub}.partner_id, {sub}.currency_id, {sub}.move_id,
                    {sub}.date, {sub}.date_maturity, {sub}.debit, {sub}.credit,
                    {sub}.name, {sub}.ref, {sub}.blocked, {sub}.company_id,
                    CASE WHEN {sub}.currency_id is not null
                        THEN {sub}.open_amount_currency
                        ELSE {sub}.open_amount
                    END as open_amount, {sub}.id
                FROM {sub}
                """,
                locals(),
            ),
            "utf-8",
        )

    def _display_outstanding_lines_sql_q3(self, sub, company_id):
        return str(
            self._cr.mogrify(
                f"""
            SELECT {sub}.partner_id, {sub}.move_id, {sub}.date,
                {sub}.date_maturity, {sub}.name, {sub}.ref, {sub}.debit,
                {sub}.credit, {sub}.debit-{sub}.credit AS amount,
                COALESCE({sub}.currency_id, c.currency_id) AS currency_id,
                {sub}.open_amount, {sub}.blocked, {sub}.id
            FROM {sub}
            JOIN res_company c ON (c.id = {sub}.company_id)
            WHERE c.id = %(company_id)s AND {sub}.open_amount != 0.0
            """,
                locals(),
            ),
            "utf-8",
        )

    def _get_account_display_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = tuple(partner_ids)
        # pylint: disable=E8103
        self.env.cr.execute(
            """
        WITH Q1 as (%s),
             Q2 AS (%s),
             Q3 AS (%s)
        SELECT partner_id, currency_id, move_id, date, date_maturity, debit,
            credit, amount, open_amount, COALESCE(name, '') as name,
            COALESCE(ref, '') as ref, blocked, id
        FROM Q3
        ORDER BY date, date_maturity, move_id"""
            % (
                self._display_outstanding_lines_sql_q1(
                    partners, date_end, account_type
                ),
                self._display_outstanding_lines_sql_q2("Q1"),
                self._display_outstanding_lines_sql_q3("Q2", company_id),
            )
        )
        for row in self.env.cr.dictfetchall():
            res[row.pop("partner_id")].append(row)
        return res

    def _add_currency_line(self, line, currency):
        if float_is_zero(line["open_amount"], precision_rounding=currency.rounding):
            return []
        return [line]

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            data = {}
        if "company_id" not in data:
            wiz = self.env["outstanding.statement.wizard"].with_context(
                active_ids=docids, model="res.partner"
            )
            data.update(wiz.create({})._prepare_statement())
        data["amount_field"] = "open_amount"
        return super()._get_report_values(docids, data)
