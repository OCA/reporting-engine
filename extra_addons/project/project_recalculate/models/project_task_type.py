# See README.rst file on addon root folder for license details

from odoo import models, fields


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    include_in_recalculate = fields.Boolean(
        string="Include in project recalculate", default=True,
        help="If you mark this check, tasks that are in this stage will be "
             "selectable for recalculating their dates when user click on "
             "'Recalculate project' button.")
