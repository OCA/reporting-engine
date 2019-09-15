# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCountryStateDistrictWard(models.Model):
    _name = 'res.country.state.district.ward'

    name = fields.Char("Name", required=True)
    code = fields.Char("Code")
    district_id = fields.Many2one(
        'res.country.state.district',
        'District',
        required=True)
