# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import models


class SqlFileWizard(models.TransientModel):
    _inherit = "sql.file.wizard"

    def export_sql(self):
        self.ensure_one()
        if self.sql_export_id.export_delta:
            self = self.with_context(export_delta_id=self.id)
        return super(SqlFileWizard, self).export_sql()
