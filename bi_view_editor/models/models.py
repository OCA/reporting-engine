# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.exceptions import Warning as UserError
from odoo.tools.translate import _


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _bi_view(self):
        return self._name[0:6] == 'x_bve.'

    @api.model
    def _auto_end(self):
        if not self._bi_view():
            super(Base, self)._auto_end()

    @api.model
    def _auto_init(self):
        if not self._bi_view():
            super(Base, self)._auto_init()

    @api.model
    def _setup_complete(self):
        if not self._bi_view():
            super(Base, self)._setup_complete()
        else:
            self.pool.models[self._name]._log_access = False

    @api.model
    def _read_group_process_groupby(self, gb, query):
        if not self._bi_view():
            return super(Base, self)._read_group_process_groupby(gb, query)

        split = gb.split(':')
        if split[0] not in self._fields:
            raise UserError(
                _('No data to be displayed.'))
        return super(Base, self)._read_group_process_groupby(gb, query)

    @api.model
    def _add_magic_fields(self):
        if self._bi_view():
            self._log_access = False
        return super(Base, self)._add_magic_fields()

    @api.model_cr
    def _table_exist(self):
        if not self._bi_view():
            return super(Base, self)._table_exist()
        return 1

    # @api.model_cr
    # def _create_table(self):
    #     if not self._bi_view():
    #         return super(Base, self)._create_table()
    #     return 1
