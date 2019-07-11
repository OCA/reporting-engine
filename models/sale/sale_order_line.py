# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    d_length = fields.Float(
        string='Length (mm)')
    d_width = fields.Float(string='Width (mm)')
    d_hight = fields.Float(string='Hight (mm)')

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        domain = super(SaleOrderLine, self).product_id_change()
        if self.product_id.standard_length and\
                self.product_id.standard_width and\
                self.product_id.standard_hight:
            self.update({'d_length': self.product_id.standard_length,
                         'd_width': self.product_id.standard_width,
                         'd_hight': self.product_id.standard_hight})
        return domain

    @api.onchange('d_length', 'd_hight', 'd_width')
    def onchange_dimension(self):
        product = self.product_id
        if not (product.standard_width or product.standard_width or
                product.standard_width):
            return
        baselocaldict = {'length': self.d_length, 'hight': self.d_hight,
                         'width': self.d_width, 'dai': self.d_length,
                         'rong': self.d_width, 'cao': self.d_hight}
        localdict = dict(baselocaldict, product=product)
        if product.condition_code:
            result = product.product_tmpl_id.satisfy_condition(localdict)
            vals = {}
            if result:
                vals.update({'product_uom': product.second_uom_id.id,
                             'product_uom_qty': 1})
            else:
                vals.update({'product_uom': product.uom_id.id})
        if product.formula:
            qty = product.product_tmpl_id._compute_by_dimension(localdict)
            if qty:
                vals.update({'product_uom_qty': qty})
        self.update(vals)
