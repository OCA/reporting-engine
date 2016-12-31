# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError


class Report(models.Model):
    _inherit = "report"

    @api.model
    def _get_report_from_name(self, report_name):
        reports = self.env['ir.actions.report.xml'].search([
            ('report_type', '!=', False),
            ('report_name', '=', report_name)])
        if not reports:
            raise UserError(_(
                "No report named '%s' found.") % report_name)
        return reports[0]
