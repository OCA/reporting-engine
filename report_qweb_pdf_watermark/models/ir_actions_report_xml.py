# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    pdf_watermark = fields.Binary('Watermark')
    pdf_watermark_expression = fields.Char(
        'Watermark expression', help='An expression yielding the base64 '
        'encoded data to be used as watermark. \n'
        'You have access to variables `env` and `docs`')
