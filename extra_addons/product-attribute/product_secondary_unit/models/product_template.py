# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    secondary_uom_ids = fields.One2many(
        comodel_name='product.secondary.unit',
        inverse_name='product_tmpl_id',
        string='Secondary Unit of Measure',
        help='Default Secondary Unit of Measure.',
    )
