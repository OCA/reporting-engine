# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[("xlsx", "xlsx")])
    header_id = fields.Many2one('report.xlsx.hf',
                                string="Header",
                                domain=[('hf_type', '=', 'header')])
    footer_id = fields.Many2one('report.xlsx.hf',
                                string="Footer",
                                domain=[('hf_type', '=', 'footer')])
