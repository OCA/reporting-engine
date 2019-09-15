# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    milestone_ids = fields.One2many('project.milestone',
                                    'project_id',
                                    string="Milestones",
                                    copy=True)
    use_milestones = fields.Boolean(help="Does this project use milestones?")
