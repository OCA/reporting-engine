# Copyright 2015 Incaser Informatica S.L. - Sergio Teruel
# Copyright 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    case_default = fields.Boolean(
        string='Default for New Projects',
        help='If you check this field, this stage will be proposed by default '
             'on each new project. It will not assign this stage to existing '
             'projects.')
