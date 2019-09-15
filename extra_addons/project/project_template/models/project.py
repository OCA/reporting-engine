# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    is_template = fields.Boolean(string="Is Template",
                                 copy=False)

    # CREATE A PROJECT FROM A TEMPLATE AND OPEN THE NEWLY CREATED PROJECT
    def create_project_from_template(self):
        if " (TEMPLATE)" in self.name:
            new_name = self.name.replace(" (TEMPLATE)", " (COPY)")

        new_project = self.copy(default={'name': new_name,
                                         'active': True,
                                         'total_planned_hours': 0.0,
                                         'alias_name': False})
        if new_project.subtask_project_id != new_project.id:
            new_project.subtask_project_id = new_project.id

        # SINCE THE END DATE DOESN'T COPY OVER ON TASKS
        # (Even when changed to copy=true), POPULATE END DATES ON THE TASK
        for new_task_record in new_project.task_ids:
            for old_task_record in self.task_ids:
                if new_task_record.name == old_task_record.name:
                    new_task_record.date_end = old_task_record.date_end

        # OPEN THE NEWLY CREATED PROJECT FORM
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.project',
            'target': 'current',
            'res_id': new_project.id,
            'type': 'ir.actions.act_window'
        }

    # ADD "(TEMPLATE)" TO THE NAME WHEN PROJECT IS MARKED AS A TEMPLATE
    @api.onchange('is_template')
    def on_change_is_template(self):
        # Add "(TEMPLATE)" to the Name if is_template == true
        # if self.name is needed for creating projects via configuration menu
        if self.name:
            if self.is_template:
                if "(TEMPLATE)" not in self.name:
                    self.name = self.name + " (TEMPLATE)"
                if self.user_id:
                    self.user_id = False
                if self.partner_id:
                    self.partner_id = False
                if self.alias_name:
                    self.alias_name = False

            else:
                if " (TEMPLATE)" in self.name:
                    self.name = self.name.replace(" (TEMPLATE)", "")
