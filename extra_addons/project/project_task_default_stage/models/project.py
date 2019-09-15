# Copyright 2015 Incaser Informatica S.L. - Sergio Teruel
# Copyright 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def _get_default_type_common(self):
        ids = self.env['project.task.type'].search([
            ('case_default', '=', True)])
        return ids

    type_ids = fields.Many2many(
        default=lambda self: self._get_default_type_common())
