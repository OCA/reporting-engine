# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class Py3oServer(models.Model):
    _name = 'py3o.server'

    url = fields.Char("URL", required=True)
    is_active = fields.Boolean("Active", default=True)
