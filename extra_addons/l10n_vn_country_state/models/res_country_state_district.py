# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCountryStateDistrict(models.Model):
    _name = 'res.country.state.district'
    _order = 'sequence, code'

    name = fields.Char("Name", required=True)
    code = fields.Char("Code")
    state_id = fields.Many2one('res.country.state', 'State', required=True)
    sequence = fields.Integer(string='Sequence')
