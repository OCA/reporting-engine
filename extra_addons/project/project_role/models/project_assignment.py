# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectAssignment(models.Model):
    _name = 'project.assignment'
    _description = 'Project Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        compute='_compute_name',
        store=True,
        index=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        related='project_id.company_id',
        store=True,
        readonly=True,
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
        required=True,
        track_visibility='onchange',
    )
    role_id = fields.Many2one(
        comodel_name='project.role',
        string='Role',
        required=True,
        track_visibility='onchange',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=True,
        track_visibility='onchange',
    )

    _sql_constraints = [
        (
            'project_role_user_uniq',
            'unique (project_id, role_id, user_id)',
            'User may be assigned per role only once within a project!'
        ),
    ]

    @api.depends('project_id.name', 'role_id.name', 'user_id.name')
    def _compute_name(self):
        for assignment in self:
            assignment.name = _('%s as %s on %s') % (
                assignment.user_id.name,
                assignment.role_id.name,
                assignment.project_id.name,
            )

    @api.multi
    @api.constrains('role_id', 'user_id')
    def _check_assignable(self):
        for assignment in self:
            if not assignment.role_id.can_assign(assignment.user_id):
                raise ValidationError(_(
                    'User %s can not be assigned to role %s.'
                ) % (
                    assignment.user_id.name,
                    assignment.role_id.name,
                ))
