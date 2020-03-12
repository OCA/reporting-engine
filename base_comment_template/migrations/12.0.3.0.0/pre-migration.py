# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    table = 'res_partner'
    old_column = 'property_comment_template_id'
    new_column = openupgrade.get_legacy_name(old_column)
    if openupgrade.column_exists(cr, table, old_column):
        openupgrade.rename_columns(cr, {table: [(old_column, new_column)]})
