# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    table = 'res_partner'
    new_column = 'property_comment_template_id'
    old_column = openupgrade.get_legacy_name(new_column)
    if openupgrade.column_exists(cr, table, old_column):
        openupgrade.convert_to_company_dependent(
            env, 'res.partner', old_column, new_column, 'res_partner')
