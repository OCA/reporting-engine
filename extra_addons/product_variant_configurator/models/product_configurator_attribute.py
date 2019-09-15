# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductConfiguratorAttribute(models.Model):
    _name = 'product.configurator.attribute'

    owner_id = fields.Integer(
        string="Owner",
        required=True,
        # ondelete is required since the owner_id is declared as inverse
        # of the field product_attribute_ids of the abstract model
        # product.configurator
        ondelete='cascade')
    owner_model = fields.Char(required=True)
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product Template',
        required=True)
    attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Attribute', readonly=True)
    value_id = fields.Many2one(
        comodel_name='product.attribute.value',
        domain="[('attribute_id', '=', attribute_id), "
               " ('id', 'in', possible_value_ids)]",
        string='Value')
    possible_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        compute='_compute_possible_value_ids',
        readonly=True)

    price_extra = fields.Float(
        digits=dp.get_precision('Product Price'),
        help="Price Extra: Extra price for the variant with this attribute "
             "value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")

    @api.depends('attribute_id')
    def _compute_possible_value_ids(self):
        for record in self:
            # This should be unique due to the new constraint added
            attribute = record.product_tmpl_id.attribute_line_ids.filtered(
                lambda x: x.attribute_id == record.attribute_id)
            record.possible_value_ids = attribute.value_ids.sorted()
