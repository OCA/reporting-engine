# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    tag_ids = fields.Many2many(
        comodel_name='product.template.tag', string="Product Tags",
        relation='product_template_product_tag_rel',
        column1='product_tmpl_id', column2='tag_id')
