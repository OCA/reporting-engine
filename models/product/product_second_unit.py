# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class ProductSecondaryUnit(models.Model):
    _name = 'product.secondary.unit'
    _description = 'Product Secondary Unit'
    _rec_name = 'uom_name'

    sequence = fields.Integer(string="Sequence", default=1)
    uom_name = fields.Char(string='Name', related='uom_id.name')
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        required=True,
    )
    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Secondary Unit of Measure',
        required=True,
        help="Default Secondary Unit of Measure.",
    )
    condition_code = fields.Text(string='Condition')
    formula = fields.Text(
        string='Formula for Price Unit',
        default='result = price_unit')
    formula_qty = fields.Text(
        string='Formula for Sale Quantity',
        default='result = 1')
    factor = fields.Float(
        string='Secondary Unit Factor',
        default=1.0,
        digits=0,
        required=True,
    )

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
    def _compute_price_unit_by_dimension(self, localdict):
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

    def _compute_by_dimension(self, localdict):
        """
        :param localdict: dictionary containing the environement in which to
        compute the rule
        :return: returns a tuple build as the base/amount computed,
        the quantity and the rate
        :rtype: float
        """
        self.ensure_one()
        if not self.formula_qty:
            return False
        else:
            try:
                safe_eval(self.formula_qty, localdict, mode='exec',
                          nocopy=True)
                return float(localdict['result'])
            except Exception as e:
                raise UserError(
                    _('Wrong python code defined for formula %s (%s).') %
                    (self.formula, e))
