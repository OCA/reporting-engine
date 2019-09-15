# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manufacturer = fields.Many2one(
        comodel_name='res.partner', string='Manufacturer',
    )
    manufacturer_pname = fields.Char(string='Manuf. Product Name')
    manufacturer_pref = fields.Char(string='Manuf. Product Code')
    manufacturer_purl = fields.Char(string='Manuf. Product URL')
