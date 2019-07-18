# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    factor = fields.Float(
        string='Ratio',
        default=1.0)
