# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _compute_chained_qty_done(self, qty=0, line=False):
        """
        Computes the net quantity done for the given move ids recursively.
        There's an optional line parameter to be able to filter by invoice line
        so we only compute the quantities related to that invoice.
        :param int qty: acumulated quantity
        :param int line: optional invoice_line object to filter moves by
        :return int: the recursive computed quantity
        """
        move_ids = self
        if line:
            move_ids = self.filtered(lambda x: x.invoice_line_id == line)
        for move in move_ids:
            if move.location_dest_id.usage == 'supplier':
                qty -= move.quantity_done
            elif move.location_dest_id.usage == 'customer':
                qty += move.quantity_done
            if move.move_dest_ids:
                qty = move.move_dest_ids._compute_chained_qty_done(qty, line)
        return qty
