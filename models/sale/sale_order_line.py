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
        vals = {}
        if product.standard_width and product.standard_height and\
                product.standard_length and product.secondary_uom_ids:
            baselocaldict = {'length': self.d_length, 'height': self.d_height,
                             'width': self.d_width, 'dai': self.d_length,
                             'rong': self.d_width, 'cao': self.d_height,
                             'price_unit': self.origin_price_unit}
            localdict = dict(baselocaldict, product=product)
            result = product.product_tmpl_id._compute_qty_unit_price(localdict)
            if result and isinstance(result, tuple):
                vals.update({'product_uom': result[0].uom_id.id,
                             'product_uom_qty': result[1],
                             'price_unit': result[2]})
            else:
                vals.update({'product_uom': product.uom_id.id,
                             'product_uom_qty': 1,
                             'price_unit': self.origin_price_unit})
        self.update(vals)

    def get_sale_order_line_multiline_description_sale(self, product):
        """Overide native Odoo"""
        if product.system_name:
            return super(SaleOrderLine, self).\
                get_sale_order_line_multiline_description_sale(product)
        pacv = self.product_custom_attribute_value_ids
        lst_name = []
        for value in product.attribute_value_ids:
            if value.name.upper() == 'KHÔNG CHỌN' or\
                    value.name.upper() == 'NO':
                continue
            custom_pacv = pacv.filtered(
                lambda cl: cl.attribute_value_id.attribute_id ==
                value.attribute_id and value.name ==
                cl.attribute_value_id.name and cl.custom_value)
            line_name = value.attribute_id.name + ': ' + value.name
            if custom_pacv:
                lst_name.append(
                    line_name + ' (' +
                    (custom_pacv[0].custom_value or '').strip() + ')')
            else:
                lst_name.append(line_name)
        if self.product_no_variant_attribute_value_ids:

            # display the no_variant attributes, except those that are also
            # displayed by a custom (avoid duplicate)
            for no_variant_attribute_value in\
                    self.product_no_variant_attribute_value_ids:
                if no_variant_attribute_value.name.upper() == 'KHÔNG CHỌN' or\
                        no_variant_attribute_value.name.upper() == 'NO':
                    continue
                line_name = no_variant_attribute_value.attribute_id.name +\
                    ': ' + no_variant_attribute_value.name
                custom_pacv = pacv.filtered(
                    lambda cl: cl.attribute_value_id.attribute_id ==
                    no_variant_attribute_value.attribute_id and
                    no_variant_attribute_value.name ==
                    cl.attribute_value_id.name and cl.custom_value)
                if custom_pacv:
                    lst_name.append(
                        line_name + ' (' +
                        (custom_pacv[0].custom_value or '').strip() + ')')
                else:
                    lst_name.append(line_name)
        if product.description_sale:
            lst_name.append(product.description_sale)
        name = "\n".join(map(str, lst_name))
        return name or product.display_name
