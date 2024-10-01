# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, api, models


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if self._context.get("access_sudo", False):
            self = self.with_user(SUPERUSER_ID)
        return super().name_search(name, args, operator, limit)

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        if self._context.get("access_sudo", False):
            self = self.with_user(SUPERUSER_ID)
        return super().search(args, offset, limit, order)

    def fetch(self, field_names):
        """Add permission to read analytic account for do something."""
        if self._context.get("access_sudo", False):
            self = self.with_user(SUPERUSER_ID)
        return super().fetch(field_names)
