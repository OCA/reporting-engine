# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr, """SELECT id, py3o_template_data FROM py3o_template"""
    )
    templates = env.cr.fetchall()
    for template_id, data in templates:
        template = env["py3o.template"].browse(template_id)
        template.write({"py3o_template_data": bytes(data)})
