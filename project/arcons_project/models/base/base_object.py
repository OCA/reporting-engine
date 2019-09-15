# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError


class BaseObjects(models.AbstractModel):
    _name = 'base.object'
    _description = 'Base Object'

    code = fields.Char(
        string='Code',
        required=True)
    name = fields.Char(
        string='Name',
        required=True)
