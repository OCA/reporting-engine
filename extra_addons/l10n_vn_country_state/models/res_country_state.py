# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'
    _order = 'sequence, code'

    sequence = fields.Integer(string='Sequence')
