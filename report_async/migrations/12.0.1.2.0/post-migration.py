from openupgradelib import openupgrade


def populate_report_async_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE queue_job qj
        SET report_async_id = ra.id
        FROM report_async ra
        WHERE qj.func_string LIKE '%report.async(' || ra.id || ',%'
          AND qj.user_id = ra.create_uid
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    populate_report_async_id(env)
