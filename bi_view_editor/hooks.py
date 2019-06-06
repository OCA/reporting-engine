# Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID
from odoo import api, modules

from odoo.tools import existing_tables, topological_sort

_logger = logging.getLogger(__name__)


def _bi_view(_name):
    return _name.startswith('x_bve.')


def post_load():

    def check_tables_exist(self, cr):
        """
        Verify that all tables are present and try to initialize
        those that are missing.
        """
        # This monkey patch is meant to avoid that the _logger writes
        # warning and error messages, while running an update all,
        # in case the model is a bi-view-generated model.

        env = api.Environment(cr, SUPERUSER_ID, {})
        table2model = {
            model._table: name for name, model in env.items()
            if not model._abstract and not _bi_view(name)  # here is the patch
        }
        missing_tables = set(table2model).difference(
            existing_tables(cr, table2model))

        if missing_tables:
            missing = {table2model[table] for table in missing_tables}
            _logger.warning("Models have no table: %s.", ", ".join(missing))
            # recreate missing tables following model dependencies
            deps = {name: model._depends for name, model in env.items()}
            for name in topological_sort(deps):
                if name in missing:
                    _logger.info("Recreate table of model %s.", name)
                    env[name].init()
            # check again, and log errors if tables are still missing
            missing_tables = set(table2model).difference(
                existing_tables(cr, table2model))
            for table in missing_tables:
                _logger.error("Model %s has no table.", table2model[table])

    modules.registry.Registry.check_tables_exist = check_tables_exist


def uninstall_hook(cr, registry):
    # delete dirty data that could cause problems
    # while re-installing the module
    cr.execute("""
        delete from ir_model where model like 'x_bve.%'
    """)
    cr.execute("""
        delete from bve_view where model_name like 'x_bve.%'
    """)
    cr.execute("""
        SELECT 'DROP VIEW ' || table_name
          FROM information_schema.views
         WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
           AND table_name like 'x_bve_%'
    """)
    results = list(cr.fetchall())
    for result in results:
        cr.execute(result[0])
