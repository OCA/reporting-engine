# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    name = fields.Char(translate=False)
    product_group_id = fields.Many2one(
        string='Product Group',
        comodel_name='product.group')
    # Dimension
    standard_length = fields.Float(
        string='Length (mm)',
        digits=dp.get_precision('Product Unit of Measure'))
    standard_width = fields.Float(string='Width (mm)')
    standard_height = fields.Float(
        string='Height (mm)',
        digits=dp.get_precision('Product Unit of Measure'))
    consum_factor = fields.Float(
        string='Consume Factor',
        digits=dp.get_precision('Product Unit of Measure'))

    price_factor = fields.Float(string='Price Factor')

    # Secondary Unit
    secondary_uom_ids = fields.One2many(
        comodel_name='product.secondary.unit',
        inverse_name='product_tmpl_id',
        string='Secondary Unit of Measure',
        help='Default Secondary Unit of Measure.',
    )
    system_name = fields.Boolean(
        string='Use System Name')

    @api.onchange('consum_factor', 'price_factor')
    def onchange_price_factor(self):
        if self.consum_factor and self.price_factor:
            self.list_price = self.consum_factor * self.price_factor

    @api.multi
    def _compute_qty_unit_price(self, localdict):
        self.ensure_one()
        result = None
        for uom in self.secondary_uom_ids.sorted(key=lambda r: r.sequence):
            if not uom.satisfy_condition(localdict):
                continue
            qty = uom._compute_by_dimension(localdict)
            unit_price = uom._compute_price_unit_by_dimension(localdict)
            result = (uom, qty, unit_price)
            break
        return result
