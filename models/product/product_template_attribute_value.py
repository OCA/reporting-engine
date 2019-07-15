# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    factor = fields.Float(string='Ratio', default=1, digits=0)
    avg_price = fields.Float(
        string='Average Price',
        digits=dp.get_precision('Product Price'),
        help="Extra Price = Average price * Ratio for the variant with "
             "this attribute value on sale price. eg. 200 price average, "
             "ratio = 1.5, 1.5*200 = 300.""")

    @api.onchange('factor', 'avg_price', 'price_extra')
    def onchange_avg_price(self):
        if self.factor and self.avg_price:
            self.price_extra = self.factor * self.avg_price
        elif self.price_extra and not self.factor and not self.avg_price:
            self.update({'factor': 1,
                         'avg_price': self.price_extra})
        elif self.price_extra and self.factor and not self.avg_price:
            self.avg_price = self.price_extra / self.factor
        elif self.price_extra and self.avg_price and not self.factor:
            self.factor = self.price_extra / self.avg_price

    @api.multi
    def btn_update_avg_price(self):
        self.ensure_one()

        view_id = self.env.ref(
            'arch_construction.view_attr_value_modify_wizard_form').id
        ctx = {
            'default_attribute_id': self.attribute_id.id,
            'default_product_tmpl_id': self.product_tmpl_id.id,
            'default_avg_price': self.avg_price
        }
        return {
            'name': _("Update Price"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'attr.value.modify.wizard',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'views': [(False, 'form')],
            'target': 'new',
        }
