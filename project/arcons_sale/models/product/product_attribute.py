# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    name = fields.Char(translate=False)
    avg_price = fields.Float(
        string='Average Price',
        digits=dp.get_precision('Product Price'))

    def btn_update_avg_price(self):
        AttrValue = self.env['product.template.attribute.value']
        for value in self.filtered(
                lambda a: a.avg_price > 0).mapped('value_ids'):
            if not value.factor:
                continue
            tmpl_attr_values = AttrValue.search(
                [('product_attribute_value_id', '=', value.id)])
            avg_price = value.attribute_id.avg_price
            for tmpl_value in tmpl_attr_values:
                tmpl_value.write({'factor': value.factor,
                                  'avg_price': avg_price,
                                  'price_extra': value.factor * avg_price *
                                  tmpl_value.unit_factor})
        return True
