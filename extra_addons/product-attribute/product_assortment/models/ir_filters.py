# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.osv import expression


class ProductAssortment(models.Model):
    _inherit = 'ir.filters'

    @api.model
    def _get_default_model(self):
        if self.env.context.get('product_assortment', False):
            model = self.env.ref('product.model_product_product')
            return model.model
        return ''

    @api.model
    def _get_default_is_assortment(self):
        if self.env.context.get('product_assortment', False):
            return True
        return False

    model_id = fields.Selection(
        default=lambda x: x._get_default_model())

    blacklist_product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='assortment_product_blacklisted')

    whitelist_product_ids = fields.Many2many(
        comodel_name='product.product',
        relation='assortment_product_whitelisted')

    record_count = fields.Integer(compute='_compute_record_count')

    is_assortment = fields.Boolean(
        default=lambda x: x._get_default_is_assortment())

    @api.multi
    def _get_eval_domain(self):
        res = super(ProductAssortment, self)._get_eval_domain()

        if self.whitelist_product_ids and res:
            result_domain = [('id', 'in', self.whitelist_product_ids.ids)]
            res = expression.OR([result_domain, res])

        if self.blacklist_product_ids:
            result_domain = [('id', 'not in', self.blacklist_product_ids.ids)]
            res = expression.AND([result_domain, res])

        return res

    @api.multi
    def _compute_record_count(self):
        for record in self:
            domain = record._get_eval_domain()
            record.record_count = self.env[
                record.model_id].search_count(domain)

    @api.model
    def _get_action_domain(self, action_id=None):
        # tricky way to act on get_filter method to prevent returning
        # assortment in search view filters
        domain = super(ProductAssortment,
                       self)._get_action_domain(action_id=action_id)
        domain = expression.AND([
            [('is_assortment', '=', False)],
            domain,
        ])

        return domain

    @api.multi
    def show_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Products"),
            'res_model': 'product.product',
            'domain': self._get_eval_domain(),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'context': self.env.context,
            'target': 'current',
        }
