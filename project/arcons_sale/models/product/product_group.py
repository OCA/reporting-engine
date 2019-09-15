# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductGroup(models.Model):
    _name = "product.group"
    _description = "Product Group"

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    note = fields.Text(string='Note')
    parent_id = fields.Many2one(
        string='Parent',
        comodel_name='product.group')
    child_ids = fields.One2many(
        string='Children',
        comodel_name='product.group',
        inverse_name='parent_id')
