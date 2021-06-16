# Copyright 2018 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, models


class ActivityStatement(models.AbstractModel):
    """Model of Activity Statement"""

    _inherit = "statement.common"
    _name = "report.partner_statement.activity_statement"
    _description = "Partner Activity Statement"

    def _initial_balance_sql_q1(self, partners, date_start, account_type):
        return str(
            self._cr.mogrify(
                """
            SELECT l.partner_id, l.currency_id, l.company_id,
            CASE WHEN l.currency_id is not null AND l.amount_currency > 0.0
                THEN sum(l.amount_currency)
                ELSE sum(l.debit)
            END as debit,
            CASE WHEN l.currency_id is not null AND l.amount_currency < 0.0
                THEN sum(-l.amount_currency)
                ELSE sum(l.credit)
            END as credit
            FROM account_move_line l
            JOIN account_move m ON (l.move_id = m.id)
            WHERE l.partner_id IN %(partners)s
                AND l.account_internal_type = %(account_type)s
                AND l.date < %(date_start)s AND not l.blocked
                AND m.state IN ('posted')
            GROUP BY l.partner_id, l.currency_id, l.amount_currency, l.company_id
        """,
                locals(),
            ),
            "utf-8",
        )

    def _initial_balance_sql_q2(self, company_id):
        return str(
            self._cr.mogrify(
                """
            SELECT Q1.partner_id, debit-credit AS balance,
            COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %(company_id)s
        """,
                locals(),
            ),
            "utf-8",
        )

    def _get_account_initial_balance(
        self, company_id, partner_ids, date_start, account_type
    ):
        balance_start = defaultdict(list)
        partners = tuple(partner_ids)
        # pylint: disable=E8103
        self.env.cr.execute(
            """WITH Q1 AS (%s), Q2 AS (%s)
        SELECT partner_id, currency_id, balance
        FROM Q2"""
            % (
                self._initial_balance_sql_q1(partners, date_start, account_type),
                self._initial_balance_sql_q2(company_id),
            )
        )
        for row in self.env.cr.dictfetchall():
            balance_start[row.pop("partner_id")].append(row)
        return balance_start

    def _display_lines_sql_q1(self, partners, date_start, date_end, account_type):
        return str(
            self._cr.mogrify(
                """
            SELECT m.name AS move_id, l.partner_id, l.date,
                CASE WHEN (aj.type IN ('sale', 'purchase'))
                    THEN l.name
                    ELSE '/'
                END as name,
                CASE
                    WHEN (aj.type IN ('sale', 'purchase')) AND l.name IS NOT NULL
                        THEN l.ref
                    WHEN aj.type IN ('sale', 'purchase') AND l.name IS NULL
                        THEN m.ref
                    WHEN (aj.type in ('bank', 'cash'))
                        THEN 'Payment'
                    ELSE ''
                END as ref,
                l.blocked, l.currency_id, l.company_id,
                CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                    THEN sum(l.amount_currency)
                    ELSE sum(l.debit)
                END as debit,
                CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                    THEN sum(l.amount_currency * (-1))
                    ELSE sum(l.credit)
                END as credit,
                CASE WHEN l.date_maturity is null
                    THEN l.date
                    ELSE l.date_maturity
                END as date_maturity
            FROM account_move_line l
            JOIN account_move m ON (l.move_id = m.id)
            JOIN account_journal aj ON (l.journal_id = aj.id)
            WHERE l.partner_id IN %(partners)s
                AND l.account_internal_type = %(account_type)s
                AND %(date_start)s <= l.date
                AND l.date <= %(date_end)s
                AND m.state IN ('posted')
            GROUP BY l.partner_id, m.name, l.date, l.date_maturity,
                CASE WHEN (aj.type IN ('sale', 'purchase'))
                    THEN l.name
                    ELSE '/'
                END,
                CASE
                    WHEN (aj.type IN ('sale', 'purchase')) AND l.name IS NOT NULL
                        THEN l.ref
                    WHEN aj.type IN ('sale', 'purchase') AND l.name IS NULL
                        THEN m.ref
                    WHEN (aj.type in ('bank', 'cash'))
                        THEN 'Payment'
                    ELSE ''
                END,
                l.blocked, l.currency_id, l.amount_currency, l.company_id
        """,
                locals(),
            ),
            "utf-8",
        )

    def _display_lines_sql_q2(self, company_id):
        return str(
            self._cr.mogrify(
                """
            SELECT Q1.partner_id, Q1.move_id, Q1.date, Q1.date_maturity,
                Q1.name, Q1.ref, Q1.debit, Q1.credit,
                Q1.debit-Q1.credit as amount, Q1.blocked,
                COALESCE(Q1.currency_id, c.currency_id) AS currency_id
            FROM Q1
            JOIN res_company c ON (c.id = Q1.company_id)
            WHERE c.id = %(company_id)s
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
        WITH Q1 AS (%s),
             Q2 AS (%s)
        SELECT partner_id, move_id, date, date_maturity, name, ref, debit,
                            credit, amount, blocked, currency_id
        FROM Q2
        ORDER BY date, date_maturity, move_id"""
            % (
                self._display_lines_sql_q1(
                    partners, date_start, date_end, account_type
                ),
                self._display_lines_sql_q2(company_id),
            )
        )
        for row in self.env.cr.dictfetchall():
            res[row.pop("partner_id")].append(row)
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            data = {}
        if "company_id" not in data:
            wiz = self.env["activity.statement.wizard"].with_context(
                active_ids=docids, model="res.partner"
            )
            data.update(wiz.create({})._prepare_statement())
        data["amount_field"] = "amount"
        return super()._get_report_values(docids, data)
