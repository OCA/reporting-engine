# Copyright 2017 Tecnativa - Carlos Dauden
# Copyright 2018 Tecnativa - David Vidal
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import float_is_zero
from collections import OrderedDict


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _sort_grouped_lines(self, lines_dic):
        return sorted(lines_dic, key=lambda x: (
            x['picking'].date, x['picking'].date_done))

    def lines_grouped_by_picking(self):
        """This prepares a data structure for printing the invoice report
        grouped by pickings."""
        self.ensure_one()
        picking_dict = OrderedDict()
        lines_dict = OrderedDict()
        sign = -1.0 if self.type == 'out_refund' else 1.0
        for line in self.invoice_line_ids:
            remaining_qty = line.quantity
            for move in line.move_line_ids:
                key = (move.picking_id, line)
                picking_dict.setdefault(key, 0)
                qty = 0
                if move.location_id.usage == 'customer':
                    qty = -move.quantity_done * sign
                elif move.location_dest_id.usage == 'customer':
                    qty = move.quantity_done * sign
                picking_dict[key] += qty
                remaining_qty -= qty
            if (not float_is_zero(
                    remaining_qty,
                    precision_rounding=line.product_id.uom_id.rounding)):
                lines_dict[line] = remaining_qty
        no_picking = [
            {'picking': False, 'line': key, 'quantity': value}
            for key, value in lines_dict.items()
        ]
        with_picking = [
            {'picking': key[0], 'line': key[1], 'quantity': value}
            for key, value in picking_dict.items()
        ]
        return no_picking + self._sort_grouped_lines(with_picking)
