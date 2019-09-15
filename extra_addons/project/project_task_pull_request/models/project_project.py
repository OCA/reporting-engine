# Copyright 2017 Specialty Medical Drugstore
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"
    _name = "project.project"

    pr_required_states = fields.Many2many(
        'project.task.type',
        'project_pr_required',
        'project_id',
        'state_id',
        'PR Required States',
    )
