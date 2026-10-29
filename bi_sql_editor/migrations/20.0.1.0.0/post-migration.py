# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env["bi.sql.view"].search(
        [("state", "in", ("model_valid", "ui_valid")), ("model_id", "!=", False)]
    )
    for view in views:
        # Include archived restrictions, so that a rule archived in 19.0
        # is relinked instead of being recreated as an active one
        restrictions = (
            env["ir.access"]
            .with_context(active_test=False)
            .search([("model_id", "=", view.model_id.id), ("group_id", "=", False)])
        )
        restriction = (
            restrictions.filtered(lambda r, view=view: r.domain == view.domain_force)[
                :1
            ]
            or restrictions[:1]
        )
        if not restriction:
            restriction = env["ir.access"].create(view._prepare_rule())
        view.rule_id = restriction
