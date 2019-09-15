# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectType(models.Model):
    _name = 'project.type'
    _description = 'Project Type'
    _rec_name = 'complete_name'

    parent_id = fields.Many2one(
        comodel_name='project.type',
        string='Parent Type'
    )
    child_ids = fields.One2many(
        comodel_name='project.type',
        inverse_name='parent_id',
        string='Subtypes'
    )
    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    complete_name = fields.Char(
        string='Complete Name',
        compute='_compute_complete_name',
        store=True
    )
    description = fields.Text(
        translate=True,
    )
    project_ok = fields.Boolean(
        string='Can be applied for projects',
        default=True
    )
    task_ok = fields.Boolean(
        string='Can be applied for tasks'
    )

    @api.constrains('parent_id')
    def check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(
                _('You cannot create recursive project types.')
            )

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for project_type in self:
            if project_type.parent_id:
                project_type.complete_name = '%s / %s' % (
                    project_type.parent_id.complete_name,
                    project_type.name
                )
            else:
                project_type.complete_name = project_type.name
