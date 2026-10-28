# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env["bi.sql.view"].search(
        [("state", "in", ("model_valid", "ui_valid")), ("model_id", "!=", False)]
    )
    for view in views:
        restriction = env["ir.access"].search(
            [("model_id", "=", view.model_id.id), ("group_id", "=", False)],
            limit=1,
        )
        if not restriction:
            restriction = env["ir.access"].create(view._prepare_rule())
        view.rule_id = restriction
