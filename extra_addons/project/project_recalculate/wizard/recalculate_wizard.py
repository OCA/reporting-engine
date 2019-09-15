# See README.rst file on addon root folder for license details

from odoo import models, fields, api


class ProjectRecalculateWizard(models.TransientModel):
    _name = 'project.recalculate.wizard'
    _description = 'Project recalculate wizard'

    project_id = fields.Many2one(
        comodel_name='project.project', readonly=True, string="Project")
    calculation_type = fields.Selection(
        string='Calculation type', related='project_id.calculation_type',
        readonly=True)
    project_date = fields.Date(readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super(ProjectRecalculateWizard, self).default_get(fields_list)
        res['project_id'] = self.env.context.get('active_id', False)
        project = self.env['project.project'].browse(res['project_id'])
        res['project_date'] = (project.date_start
                               if project.calculation_type == 'date_begin'
                               else project.date)
        return res

    def confirm_button(self):
        return self.project_id.project_recalculate()
