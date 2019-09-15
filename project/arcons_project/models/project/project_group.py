# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, api


class ProjectGroup(models.Model):
    _name = 'project.group'
    _inherit = 'base.object'
    _description = 'Project Group'

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_group_id(self):
        group_id = False
        if 'default_project_group_id' in self.env.context:
            group_id = self.env['project.group'].browse(
                self.env.context.get('default_project_group_id'))
        if not group_id:
            group_id = self.env.ref(
                'arcons_project.default_project_group_normal',
                raise_if_not_found=False)
        return group_id
