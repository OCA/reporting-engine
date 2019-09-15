# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    assignment_ids = fields.One2many(
        string='Project Assignments',
        comodel_name='project.assignment',
        inverse_name='project_id',
        track_visibility='onchange',
    )
