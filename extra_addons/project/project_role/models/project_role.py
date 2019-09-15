# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.translate import html_translate


class ProjectRole(models.Model):
    _name = 'project.role'
    _description = 'Project Role'

    name = fields.Char(
        'Name',
        translate=True,
        required=True,
    )
    description = fields.Html(
        string='Description',
        translate=html_translate,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
    )

    _sql_constraints = [
        (
            'name_company_uniq',
            'UNIQUE (name, company_id)',
            'Role with such name already exists in the company!'
        ),
        (
            'name_nocompany_uniq',
            (
                'EXCLUDE (name WITH =) WHERE ('
                '    company_id IS NULL'
                ')'
            ),
            'Shared role with such name already exists!'
        ),
    ]

    @api.multi
    @api.constrains('name')
    def _check_name(self):
        for role in self:
            if self.search_count([
                    ('company_id', '=' if role.company_id else '!=', False),
                    ('name', '=', role.name)]) > 0:
                raise ValidationError(_(
                    'Role "%s" conflicts with another role due to same name.'
                ) % (
                    role.name,
                ))

    @api.model
    def can_assign(self, user_id):
        # Extension point to check if user can be assigned to this role
        return True
