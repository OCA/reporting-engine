# Copyright (C) 2015 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SqlExport(models.Model):
    _name = "sql.export"
    _inherit = ["sql.request.mixin"]
    _description = "SQL export"

    _sql_request_groups_relation = "groups_sqlquery_rel"

    _sql_request_users_relation = "users_sqlquery_rel"

    copy_options = fields.Char(required=False, default="CSV HEADER DELIMITER ';'")

    file_format = fields.Selection([("csv", "CSV")], default="csv", required=True)

    use_properties = fields.Boolean(compute="_compute_use_properties")
    query_properties_definition = fields.PropertiesDefinition("Query Properties")
    last_execution_date = fields.Datetime(readonly=True)
    last_execution_uid = fields.Many2one(
        "res.users", string="Last execution User", readonly=True
    )

    encoding = fields.Selection(
        [
            ("utf-8", "utf-8"),
            ("utf-16", "utf-16"),
            ("windows-1252", "windows-1252"),
            ("latin1", "latin1"),
            ("latin2", "latin2"),
            ("big5", "big5"),
            ("gb18030", "gb18030"),
            ("shift_jis", "shift_jis"),
            ("windows-1251", "windows-1251"),
            ("koir8_r", "koir8_r"),
        ],
        required=True,
        default="utf-8",
    )

    keep_generated_file = fields.Boolean(
        help="Check this to keep generated export files as attachments"
    )

    def _compute_use_properties(self):
        for rec in self:
            rec.use_properties = bool(rec.query_properties_definition)

    def configure_properties(self):
        # we need a full window in order for property configuration to work, not a modal
        wiz = self.env["sql.file.wizard"].create({"sql_export_id": self.id})
        return {
            "view_mode": "form",
            "res_model": "sql.file.wizard",
            "res_id": wiz.id,
            "type": "ir.actions.act_window",
            "context": self.env.context,
        }

    def export_sql_query(self):
        self.ensure_one()
        wiz = self.env["sql.file.wizard"].create({"sql_export_id": self.id})
        # no variable input, we can return the file directly
        if not self.query_properties_definition:
            return wiz.export_sql()
        else:
            return {
                "view_mode": "form",
                "res_model": "sql.file.wizard",
                "res_id": wiz.id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": self.env.context,
            }

    def _get_file_extension(self):
        self.ensure_one()
        if self.file_format == "csv":
            return "csv"

    def csv_get_data_from_query(self, variable_dict):
        self.ensure_one()
        # Execute Request
        res = self._execute_sql_request(
            params=variable_dict, mode="stdout", copy_options=self.copy_options
        )
        if self.encoding:
            res = res.decode(self.encoding)
        return res

    def _check_execution(self):
        self.ensure_one()
        # only check execution if query does not contains variable
        if self.query_properties_definition:
            return True
        return super()._check_execution()
