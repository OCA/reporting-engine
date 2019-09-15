# Copyright 2014 Daniel Reis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


_TASK_STATE = [
    ('draft', 'New'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled')]


class ProjectTaskType(models.Model):
    """Added state in the Project Task Type."""

    _inherit = 'project.task.type'

    state = fields.Selection(_TASK_STATE, 'State')
