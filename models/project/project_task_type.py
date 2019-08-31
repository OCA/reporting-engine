# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    project_group_id = fields.Many2one(
        string='Project Group',
        comodel_name='project.group')
