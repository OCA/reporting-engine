# -*- coding: utf-8 -*-
# Copyright 2015-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import SUPERUSER_ID
from openerp.api import Environment


def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    recs = env['bi.sql.view'].search([])
    for rec in recs:
        rec.button_set_draft()
        rec.unlink()

    # delete dirty data that could cause problems
    # while re-installing the module
    # Drop materialized views
    cr.execute("""
        select relname
        from pg_class
        where relname like 'x_bi_sql_view%' and relkind='m'
        """)
    for r in cr.fetchall():
        cr.execute("""
               DROP MATERIALIZED VIEW %s
            """ % r)

    cr.execute("""
        select relname
        from pg_class
        where relname like 'x_bi_sql_view%' and relkind='r'
        """)
    for r in cr.fetchall():
        cr.execute("""
               DROP TABLE %s
            """ % r)
    cr.execute("""
        select table_name from INFORMATION_SCHEMA.views
        where table_name like 'x_bi_sql%'""")

    # Drop not materialized views
    for v in cr.fetchall():
        cr.execute("""
               DROP VIEW %s
            """ % v)

    # Drop table if uninstalling went wrong
    cr.execute("""
        delete from ir_model_fields where model like 'bi.sql.view%';
        delete from ir_model_fields where model like 'bi_sql_%';
        delete from ir_model where model like 'x_bi_sql_view.%';
        """)
