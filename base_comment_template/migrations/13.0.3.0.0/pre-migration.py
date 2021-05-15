# Copyright 2021 Tecnativa - Pedro M: Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    if openupgrade.table_exists(env.cr, "base_comment_template_res_partner_rel"):
        # Swap column names, as they were incorrect
        env.cr.execute(
            "ALTER TABLE base_comment_template_res_partner_rel "
            "RENAME base_comment_template_id TO temp"
        )
        env.cr.execute(
            "ALTER TABLE base_comment_template_res_partner_rel "
            "RENAME res_partner_id TO base_comment_template_id"
        )
        env.cr.execute(
            "ALTER TABLE base_comment_template_res_partner_rel "
            "RENAME temp TO res_partner_id"
        )
