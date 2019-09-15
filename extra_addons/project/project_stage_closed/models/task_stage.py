# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    closed = fields.Boolean(
        help="Tasks in this stage are considered closed.",
        default=False,
    )
