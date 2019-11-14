# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    def _add_manual_fields(self, model):
        super(IrModelFields, self)._add_manual_fields(model)
        if 'bi.sql.view' in self.env:
            Sql = self.env['bi.sql.view']
            if 'model_id' in Sql._fields:
                Sql.search([('model_name', '=', model._name)]
                           ).bi_sql_view_field_ids.adjust_manual_fields(model)
