# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class Py3oFusionFiletype(models.Model):
    _name = 'py3o.fusion.filetype'

    _rec_name = 'human_ext'

    fusion_ext = fields.Char("Fusion Extension", siez=8)
    human_ext = fields.Char("Human readble extension", size=8)
