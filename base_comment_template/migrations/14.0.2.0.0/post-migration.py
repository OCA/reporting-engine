# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools import parse_version


@openupgrade.migrate()
def migrate(env, version):
    if parse_version(version) == parse_version("14.0.1.0.0"):
        openupgrade.logged_query(
            env.cr,
            """
            INSERT INTO base_comment_template_res_partner_rel
            (res_partner_id, base_comment_template_id)
            SELECT SPLIT_PART(ip.res_id, ',', 2)::int AS res_partner_id,
            SPLIT_PART(ip.value_reference, ',', 2)::int AS base_comment_template_id
            FROM ir_property ip
            JOIN ir_model_fields imf ON ip.fields_id = imf.id
            JOIN res_partner rp ON rp.id = SPLIT_PART(ip.res_id, ',', 2)::int
            JOIN base_comment_template bct
                ON bct.id = SPLIT_PART(ip.value_reference, ',', 2)::int
            WHERE imf.name = 'property_comment_template_id'
            AND imf.model = 'res.partner'
            AND ip.res_id IS NOT NULL
            ON CONFLICT DO NOTHING
            """,
        )
