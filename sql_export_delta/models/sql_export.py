# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from psycopg2.sql import SQL, Identifier

from odoo import fields, models


class SqlExport(models.Model):
    _inherit = "sql.export"

    export_delta = fields.Boolean(
        string="Delta",
        help="With this checked, the full result of the query "
        "will be stored as table in the database, but the file generated will "
        "only contain rows not existing in the n-1st export",
    )

    def write(self, vals):
        """Delete previous results when we change the query"""
        if "query" in vals:
            for this in self:
                this._export_delta_cleanup(keep_last=False)
        return super().write(vals)

    def _execute_sql_request(
        self,
        params=None,
        mode="fetchall",
        rollback=True,
        view_name=False,
        copy_options="CSV HEADER DELIMITER ';'",
        header=False,
    ):
        delta_id = self.env.context.get("export_delta_id")

        if delta_id:
            original_query = self.env.cr.mogrify(self.query, params).decode("utf-8")
            result_table = self._export_delta_table_name(delta_id)
            table_query = SQL(
                "WITH result as ({0}) SELECT * INTO TABLE {1} FROM result"
            ).format(SQL(original_query), Identifier(result_table))
            previous_result_table = self._export_delta_existing_tables()[-1:]
            if previous_result_table:
                result_query = SQL("SELECT * FROM {0} EXCEPT SELECT * FROM {1}").format(
                    Identifier(result_table),
                    Identifier(previous_result_table[0]),
                )
            else:
                result_query = SQL("SELECT * FROM {0}").format(Identifier(result_table))
            self.env.cr.execute(table_query)
            # inject new query in cache for super to use
            self._cache["query"] = result_query
            result = super()._execute_sql_request(
                params=None,
                mode=mode,
                rollback=rollback,
                view_name=view_name,
                copy_options=copy_options,
                header=header,
            )
            self.invalidate_recordset(["query"])
            self._export_delta_cleanup(keep_last=True)
        else:
            result = super()._execute_sql_request(
                params=params,
                mode=mode,
                rollback=rollback,
                view_name=view_name,
                copy_options=copy_options,
                header=header,
            )

        return result

    def _export_delta_table_name(self, identifier):
        """
        Return the name of a table to store data for delta export, must end with
        {identifier}
        """
        return f"sql_export_delta_{self.id}_{identifier}"

    def _export_delta_existing_tables(self):
        """Return all table names used for storing data for delta export"""
        self.env.cr.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s",
            (self._export_delta_table_name("%"),),
        )
        return sorted(
            [name for name, in self.env.cr.fetchall()],
            key=lambda name: int(name[len(self._export_delta_table_name("")) :]),
        )

    def _export_delta_cleanup(self, keep_last=True):
        """Delete tables storing data for delta export"""
        table_names = self._export_delta_existing_tables()[: -1 if keep_last else None]
        for table_name in table_names:
            self.env.cr.execute(SQL("DROP TABLE {0}").format(Identifier(table_name)))
