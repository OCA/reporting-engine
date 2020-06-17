# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, tools


class BiSQLView(models.Model):
    _inherit = 'bi.sql.view'

    def check_manual_fields(self, model):
        # check the fields we need are defined on self, to stop it going
        # early on install / startup - particularly problematic during upgrade
        if 'group_operator' in tools.table_columns(
                self.env.cr, 'bi_sql_view_field') and\
                model._name.startswith(self._model_prefix):
            # Use SQL instead of ORM, as ORM might not be fully initialised -
            # we have no control over the order that fields are defined!
            # We are not concerned about user security rules.
            self.env.cr.execute(
                """
SELECT
    f.name,
    f.ttype,
    f.group_operator
FROM
    bi_sql_view v
    LEFT JOIN bi_sql_view_field f ON f.bi_sql_view_id = v.id
WHERE
    v.model_name = %s
;
                """, (model._name,)
                )
            sql_fields = self.env.cr.fetchall()

            for sql_field in sql_fields:
                if sql_field[0] in model._fields and\
                        sql_field[1] in ('integer', 'float') and\
                        sql_field[2]:
                    model._fields[sql_field[0]].group_operator = sql_field[2]
