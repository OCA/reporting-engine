# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.Many2one(
        string='Project',
        comodel_name='project.project')
