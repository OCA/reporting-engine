# See README.rst file on addon root folder for license details

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    calculation_type = fields.Selection(
        [('date_begin', 'Date begin'),
         ('date_end', 'Date end')],
        string='Calculation type', default=False,
        help='How to calculate tasks, with date start or date end references. '
             'If not set, "Recalculate project" button is disabled.')

    def _start_end_dates_prepare(self):
        """
            Prepare project start or end date, looking into tasks list
            and depending on project calculation_type
            - if calculation_type == 'date_begin':
                project end date = latest date from tasks end dates
            - if calculation_type == 'date_end':
                project start date = earliest date from tasks start dates

            NOTE: Do not perform any write operations to DB
        """
        vals = {}
        self.ensure_one()
        if not self.tasks:
            return vals
        # Here we consider all project task, independently from the value in
        # include_in_recalculate
        start_task = min(self.tasks, key=lambda t: t.date_start or t.date_end)
        end_task = max(self.tasks, key=lambda t: t.date_end or t.date_start)
        # Assign min/max dates if available
        if self.calculation_type == 'date_begin' and end_task.date_end:
            vals['date'] = end_task.date_end.date()
        if self.calculation_type == 'date_end' and start_task.date_start:
            vals['date_start'] = start_task.date_start.date()
        return vals

    @api.multi
    def project_recalculate(self):
        """
            Recalculate project tasks start and end dates.
            After that, recalculate new project start or end date
        """
        for project in self:
            if not project.calculation_type:
                raise UserError(_("Cannot recalculate project because your "
                                  "project doesn't have calculation type."))
            if (project.calculation_type == 'date_begin' and not
                    project.date_start):
                raise UserError(_("Cannot recalculate project because your "
                                  "project doesn't have date start."))
            if (project.calculation_type == 'date_end' and not
                    project.date):
                raise UserError(_("Cannot recalculate project because your "
                                  "project doesn't have date end."))
            project.tasks.task_recalculate()
            vals = project._start_end_dates_prepare()
            if vals:
                project.write(vals)
        return True
