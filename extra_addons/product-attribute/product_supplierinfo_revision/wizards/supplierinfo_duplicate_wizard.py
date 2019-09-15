# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ProductSupplierInfoDuplicateWizard(models.TransientModel):
    _name = 'product.supplierinfo.duplicate.wizard'
    _description = 'Product Supplier Duplicate Wizard'

    date_start = fields.Date(required=True)
    date_end = fields.Date()
    variation_percent = fields.Float(
        digits=dp.get_precision('Product Price'),
        string='Variation %',
    )

    @api.multi
    def action_apply(self):
        Supplierinfo = self.env['product.supplierinfo']
        supplierinfo_news = Supplierinfo
        for item in Supplierinfo.browse(self.env.context['active_ids']):
            supplierinfo_news |= item.copy({
                'date_start': self.date_start,
                'date_end': self.date_end,
                'previous_info_id': item.id,
                'price': item.price * (1.0 + self.variation_percent / 100.0),
            })
            item.date_end = (fields.Date.from_string(self.date_start) -
                             relativedelta(days=1))

        action = self.env.ref(
            'product.product_supplierinfo_type_action').read()[0]
        if len(supplierinfo_news) > 0:
            action['domain'] = [('id', 'in', supplierinfo_news.ids)]
        else:  # pragma: no cover
            action = {'type': 'ir.actions.act_window_close'}
        return action
