# -*- coding: utf-8 -*-
# © 2016-2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[
        ('qweb-txt', 'Text'),
        ('qweb-txt-csv', 'CSV'),
        ])

    @api.model
    def render_report(self, res_ids, name, data):
        if (
                data.get('report_type') and
                data.get('report_type').startswith('qweb-txt')):
            ext = data['report_type'].split('-')[-1]
            # That way, you can easily add qweb-txt-zpl' or others
            # without inheriting this method (you just need to do the
            # selection_add on the field 'report_type')
            return self.env['report'].get_html(res_ids, name, data=data), ext
        else:
            return super(IrActionsReportXml, self).render_report(
                res_ids, name, data)
