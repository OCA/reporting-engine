# -*- coding: utf-8 -*-
# Copyright 2015-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import SUPERUSER_ID
from openerp.api import Environment


def uninstall_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    recs = env['bi.sql.view'].search([])
    for rec in recs:
        rec.button_set_draft()
