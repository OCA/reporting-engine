# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    qty_to_process = fields.Float(
        compute='_compute_process_qty',
        inverse='_inverse_set_process_qty',
        help="Set this quantity to create a new line "
             "for this product or update the existing one."
    )

    def _inverse_set_process_qty(self):
        parent_model = self.env.context.get('parent_model')
        parent_id = self.env.context.get('parent_id')
        if parent_model:
            parent = self.env[parent_model].browse(parent_id)
            for product in self:
                quick_line = parent._get_quick_line(product)
                if quick_line:
                    parent._update_quick_line(product, quick_line)
                else:
                    parent._add_quick_line(product, quick_line._name)

    def _compute_process_qty(self):
        if not self.env.context.get('parent_id'):
            return

    @api.multi
    def button_quick_open_product(self):
        self.ensure_one()
        return {
            'name': self.display_name,
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
