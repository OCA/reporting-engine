# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class MassReportAttachment(models.Model):
    _name = 'mass.report.attachment'
    _description = u"Report generated for one record"
    _order = 'mass_report_id, id'

    @api.model
    def _referencable_models(self):
        IrModel = self.env['ir.model']
        return [(r['model'], r['name']) for r in IrModel.search([])]

    mass_report_id = fields.Many2one(
        'mass.report', string="Mass report", ondelete='cascade')
    mass_report_line_id = fields.Many2one(
        'mass.report.line', string="Report", ondelete='cascade')
    record_id = fields.Reference(_referencable_models, string=u"Record")
    report_id = fields.Many2one(
        'ir.actions.report.xml', string="Report", readonly=True,
        related='mass_report_line_id.report_id')
    attachment_id = fields.Many2one('ir.attachment', string=u"Attachment")
    queue_job_id = fields.Many2one('queue.job', string=u"Job")
    queue_job_state = fields.Selection(related='queue_job_id.state')
    queue_job_exc_info = fields.Text(related='queue_job_id.exc_info')

    @api.multi
    def unlink(self):
        for ra in self.sudo():
            ra.queue_job_id.unlink()
        return super(MassReportAttachment, self).unlink()
