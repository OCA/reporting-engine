from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    project_status = fields.Many2one('project.status', string="Project Status")
