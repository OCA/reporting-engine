# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class Report(models.Model):

    _inherit = 'report'

    @api.model
    def _get_report_from_name(self, report_name):
        """Get the first record of ir.actions.report.xml having the
        ``report_name`` as value for the field report_name.
        """
        res = super(Report, self)._get_report_from_name(report_name)
        if res:
            return res
        # maybe a py3o report
        report_obj = self.env['ir.actions.report.xml']
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(
            [('report_type', '=', 'py3o'),
             ('report_name', '=', report_name)], limit=1)
