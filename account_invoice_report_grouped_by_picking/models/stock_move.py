# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _compute_chained_qty_done(self, line, qty=0):
        for move in self.filtered(lambda x: x.invoice_line_id == line):
            if move.location_id.usage == 'customer':
                qty -= move.quantity_done
            elif move.location_dest_id.usage == 'customer':
                qty += move.quantity_done
        return qty
