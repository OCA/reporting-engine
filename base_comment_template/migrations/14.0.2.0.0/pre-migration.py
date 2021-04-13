# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M: Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools import parse_version

field_renames = [
    ("base.comment.template", "base_comment_template", "priority", "sequence"),
]


@openupgrade.migrate()
def migrate(env, version):
    if parse_version(version) == parse_version("14.0.1.0.0"):
        openupgrade.rename_fields(env, field_renames)
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
