# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import date
from odoo.exceptions import ValidationError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        group_id = self._get_default_group_id()
        res = self.stage_find(group_id and group_id.id or False).id
        return res

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain =\
            ['|', ('project_group_ids', '=', self._get_default_group_id().id),
             ('id', 'in', stages.ids)]
        stage_ids = stages._search(search_domain, order=order,
                                   access_rights_uid=SUPERUSER_ID)
        print ("========== stage_ids: ", stage_ids)
        return stages.browse(stage_ids)

    @api.model
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

    stage_id = fields.Many2one(
        string='Stage',
        comodel_name='project.stage',
        default=lambda self: self._get_default_stage_id(),
        copy=False,
        group_expand='_read_group_stage_ids',
        index=True)
    project_group_id = fields.Many2one(
        string='Project Group',
        comodel_name='project.group',
        default=_get_default_group_id)
    sale_id = fields.Many2one(
        string="Sale Order",
        comodel_name='sale.order')

    @api.model
    def create(self, vals):
        if not vals.get('stage_id'):
            vals['stage_id'] = self.stage_find(vals['project_group_id'])
        if vals.get('sale_id') and not vals.get('partner_id'):
            vals['partner_id'] =\
                self.env['sale.order'].browse(vals['sale_id']).partner_id.id
        return super(ProjectProject, self).create(vals)

    def stage_find(self, group_id, domain=None, order='sequence', limit=1):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - team_id: if set, stages must belong to this group or
              be a default case
        """
        if domain is None:  # pragma: no cover
            domain = []
        # collect all team_ids
        search_domain = ['|', ('project_group_ids', 'in', [group_id]),
                         ('case_default', '=', True)]
        # AND with the domain in parameter
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.stage'].search(search_domain, order=order,
                                                limit=limit)

    @api.multi
    def open_tasks(self):
        for project in self:
            task_types = self.env['project.task.type'].search(
                [('project_group_id', '=', project.project_group_id.id)])
            task_types.write({'project_ids': [(4, project.id)]})
        return super(ProjectProject, self).open_tasks()
