# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


@api.model
def _bi_view(_name):
    return _name.startswith('x_bve.')


_auto_init_orig = models.BaseModel._auto_init


@api.model_cr_context
def _auto_init(self):

    # This monkey patch is meant to fix an error (probably
    # introduced by https://github.com/odoo/odoo/pull/15412), while
    # running an update all. The _auto_init() method invoked during
    # an update all is the one of BaseModel, and not the one of Base.

    # This monkey patch seems not working if defined inside the post_load()

    if _bi_view(self._name):
        return
    return _auto_init_orig(self)


models.BaseModel._auto_init = _auto_init


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def _setup_complete(self):
        if not _bi_view(self._name):
            super()._setup_complete()
        else:
            self.pool.models[self._name]._log_access = False

    @api.model
    def _read_group_process_groupby(self, gb, query):
        if not _bi_view(self._name):
            return super()._read_group_process_groupby(gb, query)

        split = gb.split(':')
        if split[0] not in self._fields:
            raise UserError(
                _('No data to be displayed.'))
        return super()._read_group_process_groupby(gb, query)

    @api.model
    def _add_magic_fields(self):
        if _bi_view(self._name):
            self._log_access = False
        return super()._add_magic_fields()
