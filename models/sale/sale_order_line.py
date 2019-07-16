# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    d_length = fields.Float(
        string='Length (mm)')
    d_width = fields.Float(string='Width (mm)')
    d_height = fields.Float(string='Height (mm)')
    origin_price_unit = fields.Float(
        string='Original Price Unit',
        digits=dp.get_precision('Product Price'))

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        domain = super(SaleOrderLine, self).product_id_change()
        vals = {'origin_price_unit': self.price_unit}
        if self.product_id.standard_length and\
                self.product_id.standard_width and\
                self.product_id.standard_height:
            vals.update({'d_length': self.product_id.standard_length,
                         'd_width': self.product_id.standard_width,
                         'd_height': self.product_id.standard_height})
        self.update(vals)
        return domain

    @api.onchange('d_length', 'd_height', 'd_width')
    def onchange_dimension(self):
        product = self.product_id
        if not (product.standard_width or product.standard_height or
                product.standard_length):
            return
        baselocaldict = {'length': self.d_length, 'height': self.d_height,
                         'width': self.d_width, 'dai': self.d_length,
                         'rong': self.d_width, 'cao': self.d_height,
                         'price_unit': self.origin_price_unit}
        localdict = dict(baselocaldict, product=product)
        result = product.product_tmpl_id._compute_qty_unit_price(localdict)
        vals = {}
        if result and isinstance(result, tuple):
            vals.update({'product_uom': result[0].uom_id.id,
                         'product_uom_qty': result[1],
                         'price_unit': result[2]})
        else:
            vals.update({'product_uom': product.uom_id.id,
                         'product_uom_qty': 1,
                         'price_unit': self.origin_price_unit})
        self.update(vals)
