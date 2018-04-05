# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def _sort_grouped_lines(self, lines_dic):
        return sorted(lines_dic, key=lambda x: (
            x['picking'].date, x['picking'].date_done))

    def lines_grouped_by_picking(self):
        self.ensure_one()
        # Split lines with no pickings
        no_picking = [{'picking': False, 'line': x} for x in
                      self.invoice_line_ids.filtered(
                          lambda x: not x.move_line_ids)]
        with_picking = [{'picking': x.picking_id, 'line': x.invoice_line_id}
                        for x in self.mapped('picking_ids.move_lines') if
                        x.invoice_line_id in self.invoice_line_ids]
        return no_picking + self._sort_grouped_lines(with_picking)
