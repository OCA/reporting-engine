# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(
        env.cr, "base_comment_template_ir_model_rel"
    ) and not column_exists(env.cr, "base_comment_template", "models"):
        openupgrade.logged_query(
            env.cr,
            "ALTER TABLE base_comment_template ADD COLUMN IF NOT EXISTS models text",
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE base_comment_template template
            SET models = (
                SELECT string_agg(model.model, ',')
                FROM base_comment_template_ir_model_rel AS rel
                JOIN ir_model AS model ON rel.ir_model_id = model.id
                WHERE rel.base_comment_template_id = template.id
            )
            """,
        )
