# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        res = super(
            ProjectProject,
            self.with_context(project_copy=True)
        ).copy(default)

        mappings = self.env['project.task.copy.map'].search(
            [('new_task_id.project_id', '=', res.id)]
        )
        for task in res.tasks:
            mapping = mappings.filtered(
                lambda t: t.new_task_id.id == task.id)
            new_dependencies = []
            for dep in mapping.old_task_id.dependency_task_ids:
                dep_mapping = mappings.filtered(
                    lambda t: t.old_task_id.id == dep.id)
                new_dependencies.append(
                    dep_mapping and dep_mapping.new_task_id.id or dep.id)
            task.write({'dependency_task_ids': [(6, 0, new_dependencies)]})
        return res
