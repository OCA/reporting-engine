# -*- coding: utf-8 -*-
# © 2016-2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[('qweb-txt', 'Text')])

    @api.model
    def render_report(self, res_ids, name, data):
        if data.get('report_type') == 'qweb-txt':
            return self.env['report'].get_html(res_ids, name, data=data), 'txt'
        else:
            return super(IrActionsReportXml, self).render_report(
                res_ids, name, data)
