# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    previous_info_id = fields.Many2one(
        comodel_name='product.supplierinfo',
        string='Previous info',
        help='Relation with previous info when duplicate line',
    )
    previous_price = fields.Float(related='previous_info_id.price',
                                  string='Previous Price')
    variation_percent = fields.Float(
        compute='_compute_variation_percent',
        store=True,
        digits=dp.get_precision('Product Price'),
        string='Variation %',
    )

    @api.multi
    @api.depends('price', 'previous_info_id.price')
    def _compute_variation_percent(self):
        for line in self:
            if not (line.price and line.previous_price):
                continue
            line.variation_percent = (
                (line.price / line.previous_price - 1) * 100)
