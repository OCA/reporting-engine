
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    length = fields.Float(string='Length (mm)')
    width = fields.Float(string='Width (mm)')
    hight = fields.Float(string='Hight (mm)')
