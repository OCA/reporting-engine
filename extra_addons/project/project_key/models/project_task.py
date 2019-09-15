# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api
from odoo.osv import expression

TASK_URL = "/web#id=%s&view_type=form&model=project.task&action=%s"


class Task(models.Model):
    _inherit = 'project.task'

    key = fields.Char(
        string='key',
        size=20,
        required=False,
        index=True,
    )

    url = fields.Char(
        string='URL',
        compute="_compute_task_url",
    )

    _sql_constraints = [
        ("task_key_unique", "UNIQUE(key)", "Task key must be unique!")
    ]

    @api.multi
    def _compute_task_url(self):
        action_id = self.env.ref('project.action_view_task').id
        for task in self:
            task.url = TASK_URL % (task.id, action_id)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        get = self.env.context.get

        project_id = vals.get('project_id', False)
        if not project_id:
            project_id = get('default_project_id', False)

        if not project_id and get('active_model', False) == 'project.project':
            project_id = get('active_id', False)

        if project_id:
            project = self.env['project.project'].browse(project_id)
            vals['key'] = project.get_next_task_key()
        return super(Task, self).create(vals)

    @api.multi
    def write(self, vals):
        project_id = vals.get('project_id', False)
        if not project_id:
            return super(Task, self).write(vals)

        project = self.env['project.project'].browse(project_id)
        for task in self:
            if task.key and task.project_id.id == project.id:
                continue

            values = self.prepare_task_for_project_switch(task, project)
            super(Task, task).write(values)

        return super(Task, self).write(vals)

    def prepare_task_for_project_switch(self, task, project):
        data = {
            'key': project.get_next_task_key(),
            'project_id': project.id
        }

        if len(task.child_ids) > 0:
            data['child_ids'] = [
                (1, child.id, self.prepare_task_for_project_switch(
                    child, project
                ))
                for child in task.child_ids
            ]
        return data

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|',
                ('key', '=ilike', name + '%'),
                ('name', operator, name)
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        tasks = self.search(domain + args, limit=limit)
        return tasks.name_get()

    @api.multi
    def name_get(self):
        result = []

        for record in self:
            task_name = []
            if record.key:
                task_name.append(record.key)
            task_name.append(record.name)
            result.append((record.id, " - ".join(task_name)))

        return result
