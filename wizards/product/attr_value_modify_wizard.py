# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class AttrValueModifyWizard(models.TransientModel):
    _name = 'attr.value.modify.wizard'
    _description = 'Product Template Attribute Value Modify'

    attribute_id = fields.Many2one(
        string='Attribute',
        comodel_name='product.attribute',
        required=True)
    product_tmpl_id = fields.Many2one(
        string='Product',
        comodel_name='product.template')
    attr_value_ids = fields.Many2many(
        string='Attribute Value',
        comodel_name='product.template.attribute.value',
        relation='product_tmpl_attr_value_rel',
        column1='wz_id',
        column2='value_id')
    avg_price = fields.Float(
        string='Average Price',
        digits=dp.get_precision('Product Price'),
        help="Extra Price = Average price * Ratio for the variant with "
             "this attribute value on sale price. eg. 200 price average, "
             "ratio = 1.5, 1.5*200 = 300.""")

    def default_get(self, fields=[]):
        ctx = self.env.context
        result = super(AttrValueModifyWizard, self).default_get(fields)
        if ctx.get('default_product_tmpl_id'):
            result['product_tmpl_id'] = ctx['default_product_tmpl_id']
        if ctx.get('default_attribute_id'):
            result['attribute_id'] = ctx['default_attribute_id']
        if ctx.get('default_avg_price'):
            result['avg_price'] = ctx['default_avg_price']
        if result.get('attribute_id') and result.get('product_tmpl_id'):
            attr_value_ids = self.env[
                'product.template.attribute.value']._search(
                [('attribute_id', '=', result['attribute_id']),
                 ('product_tmpl_id', '=', result['product_tmpl_id'])])
            result['attr_value_ids'] = [(6, 0, attr_value_ids)]
        return result

    @api.onchange('avg_price')
    def onchange_avg_price(self):
        for value in self.attr_value_ids:
            value.update({'avg_price': self.avg_price,
                          'price_extra': self.avg_price * value.factor *
                          value.unit_factor})

    @api.multi
    def btn_update_avg_price(self):
        # TODO: something
        return True
