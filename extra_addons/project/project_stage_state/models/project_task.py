# Copyright 2014 Daniel Reis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProjectTask(models.Model):
    """Added state in the Project Task."""

    _inherit = 'project.task'

    state = fields.Selection(
        related='stage_id.state', store=True)
