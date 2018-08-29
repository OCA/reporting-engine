# Copyright 2017-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID
from odoo import _, api, models, modules, tools
from odoo.exceptions import UserError

from odoo.tools import (existing_tables, topological_sort)

_logger = logging.getLogger(__name__)


@api.model
def _bi_view(_name):
    return _name[0:6] == 'x_bve.'


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


@api.model_cr_context
def _auto_init(self):
    """ Initialize the database schema of ``self``:
        - create the corresponding table,
        - create/update the necessary columns/tables for fields,
        - initialize new columns on existing rows,
        - add the SQL constraints given on the model,
        - add the indexes on indexed fields,

        Also prepare post-init stuff to:
        - add foreign key constraints,
        - reflect models, fields, relations and constraints,
        - mark fields to recompute on existing records.

        Note: you should not override this method. Instead, you can modify
        the model's database schema by overriding method :meth:`~.init`,
        which is called right after this one.
    """
    # This monkey patch is meant to fix an error (probably
    # introduced by https://github.com/odoo/odoo/pull/15412), while
    # running an update all. The _auto_init() method invoked during
    # an update all is the one of BaseModel, and not the one of Base.

    # START OF patch
    if _bi_view(self._name):
        return
    # END of patch

    models.raise_on_invalid_object_name(self._name)

    # This prevents anything called by this method (in particular default
    # values) from prefetching a field for which the corresponding column
    # has not been added in database yet!
    self = self.with_context(prefetch_fields=False)

    self.pool.post_init(self._reflect)

    cr = self._cr
    parent_store_compute = False
    update_custom_fields = self._context.get('update_custom_fields', False)
    must_create_table = not tools.table_exists(cr, self._table)

    if self._auto:
        if must_create_table:
            tools.create_model_table(cr, self._table, self._description)

        if self._parent_store:
            if not tools.column_exists(cr, self._table, 'parent_left'):
                self._create_parent_columns()
                parent_store_compute = True

        self._check_removed_columns(log=False)

        # update the database schema for fields
        columns = tools.table_columns(cr, self._table)

        def recompute(field):
            _logger.info("Storing computed values of %s", field)
            recs = self.with_context(active_test=False).search([])
            recs._recompute_todo(field)

        for field in self._fields.values():
            if not field.store:
                continue

            if field.manual and not update_custom_fields:
                continue  # don't update custom fields

            new = field.update_db(self, columns)
            if new and field.compute:
                self.pool.post_init(recompute, field)

    if self._auto:
        self._add_sql_constraints()

    if must_create_table:
        self._execute_sql()

    if parent_store_compute:
        self._parent_store_compute()


models.BaseModel._auto_init = _auto_init


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _auto_init(self):
        if not _bi_view(self._name):
            super(Base, self)._auto_init()

    @api.model
    def _setup_complete(self):
        if not _bi_view(self._name):
            super(Base, self)._setup_complete()
        else:
            self.pool.models[self._name]._log_access = False

    @api.model
    def _read_group_process_groupby(self, gb, query):
        if not _bi_view(self._name):
            return super(Base, self)._read_group_process_groupby(gb, query)

        split = gb.split(':')
        if split[0] not in self._fields:
            raise UserError(
                _('No data to be displayed.'))
        return super(Base, self)._read_group_process_groupby(gb, query)

    @api.model
    def _add_magic_fields(self):
        if _bi_view(self._name):
            self._log_access = False
        return super(Base, self)._add_magic_fields()
