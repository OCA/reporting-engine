# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import _, api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    no_create_variants = fields.Boolean(
        string="Don't create variants automatically",
        help='This check disables the automatic creation of product variants '
             'for all the products of this category.',
        default=True)

    @api.onchange('no_create_variants')
    def onchange_no_create_variants(self):
        if not self.no_create_variants:
            return {'warning': {
                'title': _('Change warning!'),
                'message': _('Changing this parameter may cause'
                             ' automatic variants creation')
            }}

    @api.multi
    def write(self, values):
        res = super(ProductCategory, self).write(values)
        if ('no_create_variants' in values and
                not values.get('no_create_variants')):
            self.env['product.template'].search(
                [('categ_id', '=', self.id),
                 ('no_create_variants', '=', 'empty')]).create_variant_ids()
        return res
