# -*- coding: utf-8 -*-
# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    report_type = fields.Selection(selection_add=[("csv", "csv")])

    @api.model
    def render_csv(self, docids, data):
        report_model_name = 'report.%s' % self.report_name
        report_model = self.env.get(report_model_name)
        if report_model is None:
            raise UserError(_('%s model was not found' % report_model_name))
        return report_model.with_context({
            'active_model': self.model
        }).create_csv_report(docids, data)
