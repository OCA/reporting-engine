# -*- coding: utf-8 -*-
# © 2016-2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class Report(models.Model):
    _inherit = "report"

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(Report, self)._get_report_from_name(report_name)
        if not res:
            res = self.env['ir.actions.report.xml'].search([
                ('report_type', '!=', False),
                ('report_name', '=', report_name)], limit=1)
        return res
