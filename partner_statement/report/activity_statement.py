# Copyright 2018 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import _, api, models

from .outstanding_statement import OutstandingStatement


class ActivityStatement(models.AbstractModel):
    """Model of Activity Statement"""

    _inherit = "statement.common"
    _name = "report.partner_statement.activity_statement"
    _description = "Partner Activity Statement"

    def _initial_balance_sql_q1(self, partners, date_start, account_type):
        return str(
            self._cr.mogrify(
                """
            SELECT l.partner_id, l.currency_id, l.company_id, l.id,
                CASE WHEN l.balance > 0.0
                    THEN l.balance - sum(coalesce(pd.amount, 0.0))
                    ELSE l.balance + sum(coalesce(pc.amount, 0.0))
                END AS open_amount,
                CASE WHEN l.balance > 0.0
                    THEN l.amount_currency - sum(coalesce(
                        pd.debit_amount_currency, 0.0)
                    )
                    ELSE l.amount_currency + sum(coalesce(
                        pc.credit_amount_currency, 0.0)
                    )
                END AS open_amount_currency
            FROM account_move_line l
            JOIN account_account aa ON (aa.id = l.account_id)
            JOIN account_move m ON (l.move_id = m.id)
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.credit_move_id = l2.id
                WHERE l2.date < %(date_start)s
            ) as pd ON pd.debit_move_id = l.id
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.debit_move_id = l2.id
                WHERE l2.date < %(date_start)s
            ) as pc ON pc.credit_move_id = l.id
            WHERE l.partner_id IN %(partners)s
                AND l.date < %(date_start)s AND not l.blocked
                AND m.state IN ('posted')
                AND aa.account_type = %(account_type)s
                AND (
                    (pd.id IS NOT NULL AND
                        pd.max_date < %(date_start)s) OR
                    (pc.id IS NOT NULL AND
                        pc.max_date < %(date_start)s) OR
                    (pd.id IS NULL AND pc.id IS NULL)
                )
            GROUP BY l.partner_id, l.currency_id, l.company_id, l.balance, l.id
        """,
                locals(),
            ),
            "utf-8",
        )

    def _initial_balance_sql_q2(self, sub):
        return str(
            self._cr.mogrify(
                f"""
            SELECT {sub}.partner_id, {sub}.currency_id,
                sum(CASE WHEN {sub}.currency_id is not null
                    THEN {sub}.open_amount_currency
                    ELSE {sub}.open_amount
                END) as balance, {sub}.company_id
            FROM {sub}
            GROUP BY {sub}.partner_id, {sub}.currency_id, {sub}.company_id""",
                locals(),
            ),
            "utf-8",
        )

    def _initial_balance_sql_q3(self, sub, company_id):
        return str(
            self._cr.mogrify(
                f"""
            SELECT {sub}.partner_id, {sub}.balance,
                COALESCE({sub}.currency_id, c.currency_id) AS currency_id
            FROM {sub}
            JOIN res_company c ON (c.id = {sub}.company_id)
            WHERE c.id = %(company_id)s""",
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
            """WITH Q1 AS ({}),
                    Q2 AS ({}),
                    Q3 AS ({})
        SELECT partner_id, currency_id, sum(balance) as balance
        FROM Q3
        GROUP BY partner_id, currency_id""".format(
                self._initial_balance_sql_q1(partners, date_start, account_type),
                self._initial_balance_sql_q2("Q1"),
                self._initial_balance_sql_q3("Q2", company_id),
            )
        )
        for row in self.env.cr.dictfetchall():
            balance_start[row.pop("partner_id")].append(row)
        return balance_start

    def _display_activity_lines_sql_q1(
        self, partners, date_start, date_end, account_type
    ):
        payment_ref = _("Payment")
        return str(
            self._cr.mogrify(
                """
            SELECT m.name AS move_id, l.partner_id, l.date,
                array_agg(l.id ORDER BY l.id) as ids,
                CASE WHEN (aj.type IN ('sale', 'purchase'))
                    THEN l.name
                    ELSE '/'
                END as name,
                CASE
                    WHEN (aj.type IN ('sale', 'purchase')) AND l.name IS NOT NULL
                        THEN l.ref
                    WHEN (aj.type in ('bank', 'cash'))
                        THEN %(payment_ref)s
                    ELSE m.ref
                END as case_ref,
                l.blocked, l.currency_id, l.company_id,
                sum(CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                    THEN l.amount_currency
                    ELSE l.debit
                END) as debit,
                sum(CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                    THEN l.amount_currency * (-1)
                    ELSE l.credit
                END) as credit,
                CASE WHEN l.date_maturity is null
                    THEN l.date
                    ELSE l.date_maturity
                END as date_maturity
            FROM account_move_line l
            JOIN account_account aa ON (aa.id = l.account_id)
            JOIN account_move m ON (l.move_id = m.id)
            JOIN account_journal aj ON (l.journal_id = aj.id)
            WHERE l.partner_id IN %(partners)s
                AND %(date_start)s <= l.date
                AND l.date <= %(date_end)s
                AND m.state IN ('posted')
                AND aa.account_type = %(account_type)s
            GROUP BY l.partner_id, m.name, l.date, l.date_maturity,
                CASE WHEN (aj.type IN ('sale', 'purchase'))
                    THEN l.name
                    ELSE '/'
                END, case_ref, l.blocked, l.currency_id, l.company_id
        """,
                locals(),
            ),
            "utf-8",
        )

    def _display_activity_lines_sql_q2(self, sub, company_id):
        return str(
            self._cr.mogrify(
                f"""
            SELECT {sub}.partner_id, {sub}.move_id, {sub}.date, {sub}.date_maturity,
                {sub}.name, {sub}.case_ref as ref, {sub}.debit, {sub}.credit, {sub}.ids,
                {sub}.debit-{sub}.credit as amount, {sub}.blocked,
                COALESCE({sub}.currency_id, c.currency_id) AS currency_id
            FROM {sub}
            JOIN res_company c ON (c.id = {sub}.company_id)
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
        WITH Q1 AS ({}),
             Q2 AS ({})
        SELECT partner_id, move_id, date, date_maturity, ids,
            COALESCE(name, '') as name, COALESCE(ref, '') as ref,
            debit, credit, amount, blocked, currency_id
        FROM Q2
        ORDER BY date, date_maturity, move_id""".format(
                self._display_activity_lines_sql_q1(
                    partners, date_start, date_end, account_type
                ),
                self._display_activity_lines_sql_q2("Q1", company_id),
            )
        )
        for row in self.env.cr.dictfetchall():
            res[row.pop("partner_id")].append(row)
        return res

    def _display_activity_reconciled_lines_sql_q1(self, sub):
        return str(
            self._cr.mogrify(
                f"""
            SELECT unnest(ids) as id
            FROM {sub}
        """,
                locals(),
            ),
            "utf-8",
        )

    def _display_activity_reconciled_lines_sql_q2(self, sub, date_end):
        return str(
            self._cr.mogrify(
                f"""
            SELECT l.id as rel_id, m.name AS move_id, l.partner_id, l.date, l.name,
                l.blocked, l.currency_id, l.company_id, {sub}.id,
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
                THEN sum(coalesce(pc.amount, 0.0))
                ELSE -sum(coalesce(pd.amount, 0.0))
            END AS open_amount,
            CASE WHEN l.balance > 0.0
                THEN sum(coalesce(pc.debit_amount_currency, 0.0))
                ELSE -sum(coalesce(pd.credit_amount_currency, 0.0))
            END AS open_amount_currency,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
            FROM {sub}
            LEFT JOIN account_partial_reconcile pd ON (
                pd.debit_move_id = {sub}.id AND pd.max_date <= %(date_end)s)
            LEFT JOIN account_partial_reconcile pc ON (
                pc.credit_move_id = {sub}.id AND pc.max_date <= %(date_end)s)
            LEFT JOIN account_move_line l ON (
                pd.credit_move_id = l.id OR pc.debit_move_id = l.id)
            LEFT JOIN account_move m ON (l.move_id = m.id)
            WHERE l.date <= %(date_end)s AND m.state IN ('posted')
            GROUP BY l.id, l.partner_id, m.name, l.date, l.date_maturity, l.name,
                CASE WHEN l.ref IS NOT NULL
                    THEN l.ref
                    ELSE m.ref
                END, {sub}.id,
                l.blocked, l.currency_id, l.balance, l.amount_currency, l.company_id
        """,
                locals(),
            ),
            "utf-8",
        )

    def _get_account_display_reconciled_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        partners = tuple(partner_ids)

        # pylint: disable=E8103
        self.env.cr.execute(
            """
        WITH Q1 AS ({}),
             Q2 AS ({}),
             Q3 AS ({}),
             Q4 AS ({}),
             Q5 AS ({}),
             Q6 AS ({})
        SELECT partner_id, currency_id, move_id, date, date_maturity, debit,
               credit, amount, open_amount, COALESCE(name, '') as name,
               COALESCE(ref, '') as ref, blocked, id
        FROM Q6
        ORDER BY date, date_maturity, move_id""".format(
                self._display_activity_lines_sql_q1(
                    partners, date_start, date_end, account_type
                ),
                self._display_activity_lines_sql_q2("Q1", company_id),
                self._display_activity_reconciled_lines_sql_q1("Q2"),
                self._display_activity_reconciled_lines_sql_q2("Q3", date_end),
                self._display_outstanding_lines_sql_q2("Q4"),
                self._display_outstanding_lines_sql_q3("Q5", company_id),
            )
        )
        return self.env.cr.dictfetchall()

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


ActivityStatement._display_outstanding_lines_sql_q2 = (
    OutstandingStatement._display_outstanding_lines_sql_q2
)
ActivityStatement._display_outstanding_lines_sql_q3 = (
    OutstandingStatement._display_outstanding_lines_sql_q3
)
