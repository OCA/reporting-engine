# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Dimension
    length = fields.Float(string='Length (mm)')
    width = fields.Float(string='Width (mm)')
    hight = fields.Float(string='Hight (mm)')
