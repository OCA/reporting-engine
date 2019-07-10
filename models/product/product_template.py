# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_group_id = fields.Many2one(
        string='Product Group',
        comodel_name='product.group')
    # Dimension
    standard_length = fields.Float(
        string='Length (mm)',
        digits=dp.get_precision('Product Unit of Measure'))
    standard_width = fields.Float(string='Width (mm)')
    standard_hight = fields.Float(
        string='Hight (mm)',
        digits=dp.get_precision('Product Unit of Measure'))
    consum_factor = fields.Float(
        string='Consume Factor', default=1.00,
        digits=dp.get_precision('Product Unit of Measure'))

    price_factor = fields.Float(string='Price Factor', default=1.00)

    # Secondary Unit
    second_uom_id = fields.Many2one(
        string='Secondary Unit of Measure',
        comodel_name='uom.uom')
    condition_code = fields.Text(
        string='Conditions')

    # Formula
    formula = fields.Text(string='Formula for Sale Quantity')

    @api.onchange('consum_factor', 'price_factor')
    def onchange_price_factor(self):
        if self.consum_factor and self.price_factor:
            self.list_price = self.consum_factor * self.price_factor

    @api.multi
    def satisfy_condition(self, localdict):
        """
        @param contract_id: id of hr.contract to be tested
        @return: returns True if the given rule match the condition for
        the given contract. Return False otherwise.
        """
        self.ensure_one()

        if not self.condition_code:
            return True
        else:
            try:
                safe_eval(self.condition_code, localdict, mode='exec',
                          nocopy=True)
                return 'result' in localdict and localdict['result'] or False
            except Exception as e:
                raise UserError(
                    _('Wrong python condition defined for condition %s (%s).')
                    % (self.condition_code, e))

    @api.multi
    def _compute_by_dimension(self, localdict):
        """
        :param localdict: dictionary containing the environement in which to
        compute the rule
        :return: returns a tuple build as the base/amount computed,
        the quantity and the rate
        :rtype: float
        """
        self.ensure_one()
        if not self.formula:
            return False
        else:
            try:
                safe_eval(self.formula, localdict, mode='exec', nocopy=True)
                return float(localdict['result'])
            except Exception as e:
                raise UserError(
                    _('Wrong python code defined for formula %s (%s).') %
                    (self.formula, e))
