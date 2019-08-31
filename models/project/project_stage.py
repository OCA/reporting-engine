# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ProjectStage(models.Model):
    _name = "project.stage"
    _description = "Project Stage"
    _order = 'sequence'

    name = fields.Char(
        string='Name',
        required=True,
        translation=True)
    sequence = fields.Integer(
        string='Sequence',
        required=True)
    department_id = fields.Many2one(
        'hr.department',
        string='Department')
    lead_time = fields.Float(
        string='Lead Time(Day)',
        digits=(16, 2))
    # technical
    validate_function = fields.Char(
        string='Validate Function',
        help='Technical Field which help run workflow')
    execute_function = fields.Char(
        string='Execute Function')
    first_stage = fields.Boolean(string="First Stage")
    last_stage = fields.Boolean(string="Last Stage")
    cancel_stage = fields.Boolean(string="Cancel Stage")
    # permission
    allow_cancel = fields.Boolean(string="Allow Cancel")
    allow_modified = fields.Boolean(string="Allow Modified")
    allow_deleted = fields.Boolean(string="Allow Deleted")
    case_default = fields.Boolean(
        string='Common to All Teams',
        help="If you check this field, this stage will be proposed by default "
             "on each sales team. It will not assign this stage to existing "
             "teams.")
    project_group_ids = fields.Many2many(
        string='Project Group',
        comodel_name='project.group',
        relation='project_stage_group_rel')
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='This stage is folded in the kanban view when '
             'there are no records in that stage to display.')
