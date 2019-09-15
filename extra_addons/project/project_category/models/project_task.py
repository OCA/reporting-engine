from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    type_id = fields.Many2one(
        comodel_name='project.type',
        string='Type',
        domain="[('task_ok', '=', True)]",
    )
