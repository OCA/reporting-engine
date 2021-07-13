# Copyright 2018 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class OutstandingStatement(models.AbstractModel):
    """Model of Outstanding Statement"""

    _inherit = "statement.common"
    _name = "report.partner_statement.outstanding_statement"
    _description = "Partner Outstanding Statement"

    def _display_lines_sql_q1(self, partners, date_end, account_type):
        partners = tuple(partners)
        return str(
            self._cr.mogrify(
                """
        SELECT l.id, m.name AS move_id, l.partner_id, l.date, l.name,
            l.blocked, l.currency_id, l.company_id,
            CASE WHEN l.ref IS NOT NULL THEN l.ref ELSE m.ref END as ref,
            CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                THEN avg(l.amount_currency)
                ELSE avg(l.debit)
            END as debit,
            CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                THEN avg(-l.amount_currency)
                ELSE avg(l.credit)
            END as credit,
            (abs(COALESCE(l.balance, 0.0)) + sum(
                coalesce(pr.pr_sign, 0.0) * coalesce(pr.amount, 0.0))
            ) * sign(COALESCE(l.balance, 0.0)) AS open_amount,
            (abs(COALESCE(l.amount_currency, 0.0)) + sum(
                coalesce(pr.pr_sign, 0.0) * CASE
                    WHEN pr.currency_id IS NOT NULL AND pr.currency_id = l.currency_id
                    THEN coalesce(pr.amount_currency, 0.0)
                    WHEN cur.id IS NOT NULL AND ROUND(
                        abs(COALESCE(l.balance, 0.0)), cur.decimal_places) > 0.0
                    THEN ROUND(coalesce(pr.amount, 0.0) *
                            COALESCE(l.amount_currency, 0.0) / NULLIF(l.balance, 0.0),
                        cur.decimal_places)
                    ELSE ROUND(coalesce(pr.amount, 0.0) *
                        COALESCE((
                            SELECT r.rate FROM res_currency_rate r
                            JOIN account_move_line aml
                                ON pr.credit_move_id = aml.id
                            WHERE r.currency_id = l.currency_id
                                AND r.name <= aml.date
                                AND (r.company_id IS NULL
                                    OR r.company_id = l.company_id)
                            ORDER BY r.company_id, r.name DESC LIMIT 1), 1.0),
                        cur.decimal_places)
                    END)
            ) * sign(COALESCE(l.amount_currency, 0.0)) AS open_amount_currency,
            CASE WHEN l.date_maturity is null
                THEN l.date
                ELSE l.date_maturity
            END as date_maturity
        FROM (
            SELECT l.*, CASE
                WHEN l.debit = 0.0 AND l.credit = 0.0 AND l.currency_id IS NOT NULL
                    AND ROUND(COALESCE(l.amount_currency, 0.0),
                        cur.decimal_places) > 0.0 THEN 1
                WHEN l.debit = 0.0 AND l.credit = 0.0 AND l.currency_id IS NOT NULL
                    AND ROUND(COALESCE(l.amount_currency, 0.0),
                        cur.decimal_places) < 0.0 THEN -1
                WHEN l.balance > 0.0 THEN 1 ELSE -1 END as sign
            FROM account_move_line l
            LEFT JOIN res_currency cur ON cur.id = l.currency_id
            ) l
        JOIN account_move m ON l.move_id = m.id
        LEFT JOIN res_currency cur ON cur.id = l.currency_id
        LEFT JOIN LATERAL (SELECT pr.*,
            CASE WHEN pr.credit_move_id = l.id THEN l.sign
                ELSE -l.sign END AS pr_sign
            FROM account_partial_reconcile pr
            WHERE pr.max_date <= %(date_end)s AND (
                (pr.debit_move_id = l.id) OR (pr.credit_move_id = l.id))
        ) as pr ON TRUE
        WHERE l.partner_id IN %(partners)s
            AND l.account_internal_type = %(account_type)s
            AND (
              (pr.id IS NOT NULL AND pr.max_date <= %(date_end)s) OR
              (pr.id IS NULL)
            ) AND l.date <= %(date_end)s AND m.state IN ('posted')
        GROUP BY l.id, l.partner_id, m.name, l.date, l.date_maturity, l.name,
            CASE WHEN l.ref IS NOT NULL THEN l.ref ELSE m.ref END,
            l.blocked, l.currency_id, l.balance, l.amount_currency, l.company_id
            """,
                locals(),
            ),
            "utf-8",
        )

    def _display_lines_sql_q2(self):
        return str(
            self._cr.mogrify(
                """
                SELECT Q1.partner_id, Q1.currency_id, Q1.move_id,
                    Q1.date, Q1.date_maturity, Q1.debit, Q1.credit,
                    Q1.name, Q1.ref, Q1.blocked, Q1.company_id,
                CASE WHEN Q1.currency_id is not null
                    THEN Q1.open_amount_currency
                    ELSE Q1.open_amount
                END as open_amount
                FROM Q1
                """,
                locals(),
            ),
            "utf-8",
        )

    def _display_lines_sql_q3(self, company_id):
        return str(
            self._cr.mogrify(
                """
            SELECT Q2.partner_id, Q2.move_id, Q2.date, Q2.date_maturity,
              Q2.name, Q2.ref, Q2.debit, Q2.credit,
              Q2.debit-Q2.credit AS amount, blocked,
              COALESCE(Q2.currency_id, c.currency_id) AS currency_id,
              Q2.open_amount
            FROM Q2
            JOIN res_company c ON (c.id = Q2.company_id)
            JOIN res_currency cur ON cur.id = COALESCE(Q2.currency_id, c.currency_id)
            WHERE c.id = %(company_id)s AND
                round(Q2.open_amount, cur.decimal_places) != 0.0
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
                            credit, amount, open_amount, name, ref, blocked
        FROM Q3
        ORDER BY date, date_maturity, move_id"""
            % (
                self._display_lines_sql_q1(partners, date_end, account_type),
                self._display_lines_sql_q2(),
                self._display_lines_sql_q3(company_id),
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
            wiz = self.env["outstanding.statement.wizard"].with_context(
                active_ids=docids, model="res.partner"
            )
            data.update(wiz.create({})._prepare_statement())
        data["amount_field"] = "open_amount"
        return super()._get_report_values(docids, data)
