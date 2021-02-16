# Copyright 2020 NextERP Romania SRL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Not tested
    properties = env["ir.property"].search(
        [
            (
                "fields_id",
                "=",
                env.ref("base.field_res_partner_property_comment_template_id").id,
            )
        ]
    )
    if properties:
        for template in properties.mapped("value_reference"):
            if not template:
                continue
            template_id = template.split(",")[-1]
            if template_id:
                template = env["base.comment.template"].browse(template_id)
                part_prop = properties.filtered(lambda p: p.value_reference == template)
                template.partner_ids = [
                    (prop["res_id"] or "").split(",")[-1] for prop in part_prop
                ]
