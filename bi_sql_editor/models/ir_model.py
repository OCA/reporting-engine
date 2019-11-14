# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    def _add_manual_fields(self, model):
        super(IrModelFields, self)._add_manual_fields(model)
        if 'bi.sql.view' in self.env:
            Sql = self.env['bi.sql.view']
            if hasattr(Sql, 'check_manual_fields'):
                Sql.check_manual_fields(model)
