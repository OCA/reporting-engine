# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class MassReportLine(models.Model):
    _name = 'mass.report.line'
    _description = u"Ordered reports to generate for one record"
    _order = 'mass_report_id, sequence'

    mass_report_id = fields.Many2one(
        'mass.report', string="Mass report", ondelete='cascade')
    model = fields.Char(u"Model", related='mass_report_id.model_id.model')
    sequence = fields.Integer(u"Sequence")
    report_id = fields.Many2one(
        'ir.actions.report.xml', string="Report", required=True)
