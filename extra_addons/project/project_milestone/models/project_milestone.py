# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class ProjectMilestone(models.Model):
    _name = 'project.milestone'
    _order = 'project_id,sequence'
    _description = 'Project Milestone'

    name = fields.Char(string="Milestone", required=True)
    target_date = fields.Date(
        help="The date when the Milestone should be complete.")
    progress = fields.Float(
        compute="_compute_milestone_progress",
        store=True,
        help="Percentage of Completed Tasks vs Incomplete Tasks.")
    project_id = fields.Many2one('project.project',
                                 string="Project",
                                 index=True)
    project_task_ids = fields.One2many('project.task',
                                       'milestone_id',
                                       string="Project Tasks")
    fold = fields.Boolean(string="Kanban Folded?")
    sequence = fields.Integer()

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('project.milestone') or 0
        vals['sequence'] = seq
        return super(ProjectMilestone, self).create(vals)

    @api.depends('project_task_ids.stage_id')
    def _compute_milestone_progress(self):
        total_tasks_count = 0.0
        closed_tasks_count = 0.0
        for record in self:
            for task_record in record.project_task_ids:
                total_tasks_count += 1
                if task_record.stage_id.closed:
                    closed_tasks_count += 1
            if total_tasks_count > 0:
                record.progress = (
                    closed_tasks_count / total_tasks_count) * 100
            else:
                record.progress = 0.0
