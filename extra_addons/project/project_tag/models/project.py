# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    tag_ids = fields.Many2many('project.tags', string="Tags",)
