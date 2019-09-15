# Copyright 2016-2018 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    priority = fields.Selection(selection_add=[
        ('2', 'High'),
        ('3', 'Very High')
    ])
