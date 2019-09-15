# -*- coding: utf-8 -*-
# © 2009 Akretion,Guewen Baconnier,Camptocamp,Avanzosc,Sharoon Thomas,Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    categ_id = fields.Many2one(string='Pricing/Primary Category')
    categ_ids = fields.Many2many(
        comodel_name='product.category', relation='product_categ_rel',
        column1='product_id', column2='categ_id', string='Extra categories')
