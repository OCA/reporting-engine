from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "sql_export_mail", "migrations/16.0.1.0.0/noupdate_changes.xml"
    )
