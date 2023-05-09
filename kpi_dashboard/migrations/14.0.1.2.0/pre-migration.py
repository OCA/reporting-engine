# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """We need to do the changes on pre-migration in order to avoid cascades"""
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_ui_view as iuv
            SET type = 'kpi_dashboard'
            FROM ir_model_data as imd
            WHERE
                iuv.id = imd.res_id
                AND imd.module = 'kpi_dashboard'
                AND imd.name = 'kpi_dashboard_dashboard_view'
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_act_window
        SET view_mode = 'kpi_dashboard'
        WHERE view_mode = 'dashboard' AND res_model = 'kpi.dashboard'
""",
    )
