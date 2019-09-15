# Copyright (C) 2017 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    firmware_version = fields.Char(
        string='Firmware Version'
    )
