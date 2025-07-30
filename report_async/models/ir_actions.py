# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import SUPERUSER_ID, api, models


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if self.env.context.get("access_sudo"):
            self = self.with_user(SUPERUSER_ID)
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None):
        if self.env.context.get("access_sudo"):
            self = self.with_user(SUPERUSER_ID)
        return super()._search(domain=domain, offset=offset, limit=limit, order=order)

    def fetch(self, field_names):
        """Add permission to read analytic account for do something."""
        if self.env.context.get("access_sudo"):
            self = self.with_user(SUPERUSER_ID)
        return super().fetch(field_names=field_names)
