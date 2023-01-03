# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo.tools.sql import column_exists


@openupgrade.migrate()
def migrate(env, version):
    if not column_exists(env.cr, "base_comment_template", "models"):
        openupgrade.logged_query(
            env.cr,
            "ALTER TABLE report_paperformat_label ADD COLUMN name char",
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE report_paperformat_label rpfl
            SET name = rpf.name
            FROM report_paperformat rpf
            WHERE rpfl.name is null
            AND rpfl.paperformat_id = rpf.id;
            """,
        )

    if not column_exists(env.cr, "ir_act_server", "label_template_view_id"):
        openupgrade.logged_query(
            env.cr,
            "ALTER TABLE ir_act_server ADD COLUMN label_template_view_id integer;",
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE ir_act_server ias
            SET label_template_view_id = iuv.id
            FROM ir_ui_view iuv
            WHERE ias.label_template is not null
            AND iuv.key = ias.label_template;
            """,
        )
