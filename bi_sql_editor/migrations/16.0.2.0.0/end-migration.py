# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    for view in env["bi.sql.view"].search([("state", "=", "ui_valid")]):
        # create new Form view
        view.form_view_id = env["ir.ui.view"].create(view._prepare_form_view()).id
        # Update tree view, to add sum / avg option
        view.tree_view_id.write(view._prepare_tree_view())
