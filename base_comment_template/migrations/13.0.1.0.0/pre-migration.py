# Copyright 2020 NextERP Romania SRL
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Not tested
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO base_comment_template_res_partner_rel
        (res_partner_id, base_comment_template_id)
        SELECT SPLIT_PART(ip.res_id, ',', 2)::int AS res_partner_id,
        SPLIT_PART(ip.value_reference, ',', 2)::int AS base_comment_template_id
        FROM ir_property ip
        JOIN ir_model_fields imf ON ip.fields_id = imf.id
        WHERE imf.name = 'property_comment_template_id'
        AND imf.model = 'res.partner'
        """,
    )
