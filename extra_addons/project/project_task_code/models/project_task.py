# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    code = fields.Char(
        string='Task Number',
        required=True,
        default='/',
        readonly=True,
    )

    _sql_constraints = [
        (
            'project_task_unique_code',
            'UNIQUE (code)',
            _('The code must be unique!')
        ),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', '/') == '/':
                vals['code'] = self.env['ir.sequence'].next_by_code(
                    'project.task'
                )
        return super().create(vals_list)

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default['code'] = self.env['ir.sequence'].next_by_code('project.task')
        return super().copy(default)

    def name_get(self):
        result = super().name_get()
        new_result = []

        for task in result:
            rec = self.browse(task[0])
            name = '[%s] %s' % (rec.code, task[1])
            new_result.append((rec.id, name))
        return new_result
