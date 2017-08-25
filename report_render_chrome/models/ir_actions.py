# -*- coding: utf-8 -*-

from openerp import models, fields


class IrActions(models.Model):
    _inherit = 'ir.actions.report.xml'

    is_chrome_pdf = fields.Boolean(string='Render using Chrome')
