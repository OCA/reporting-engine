from odoo import models, fields


class QueueJob(models.Model):
    _inherit = 'queue.job'

    report_async_id = fields.Many2one(
        comodel_name='report.async',
        string='Report Async',
        index=True,
        ondelete='cascade',
    )
