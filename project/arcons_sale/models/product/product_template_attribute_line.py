# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"

    @api.onchange('attribute_id')
    def onchange_attribute_id(self):
        AttrValue = self.env['product.attribute.value']
        value_ids = AttrValue._search(
            [('attribute_id', '=', self.attribute_id.id)])
        if value_ids:
            self.value_ids = [(6, 0, value_ids)]
