# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError
from unittest import mock

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tools.misc import mute_logger

_module_ns = 'odoo.addons.project_role'
_project_role_class = _module_ns + '.models.project_role.ProjectRole'


class TestProjectRole(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.now = fields.Datetime.now()
        self.Company = self.env['res.company']
        self.SudoCompany = self.Company.sudo()
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.Role = self.env['project.role']
        self.SudoRole = self.Role.sudo()
        self.Assignment = self.env['project.assignment']
        self.SudoAssignment = self.Assignment.sudo()

    def test_1(self):
        project = self.SudoProject.create({
            'name': 'Project #1',
        })
        role = self.SudoRole.create({
            'name': 'Role #1',
        })
        self.SudoAssignment.create({
            'project_id': project.id,
            'role_id': role.id,
            'user_id': self.env.user.id,
        })

    def test_2(self):
        project = self.SudoProject.create({
            'name': 'Project #2',
        })
        role = self.SudoRole.create({
            'name': 'Role #2',
        })
        self.SudoAssignment.create({
            'project_id': project.id,
            'role_id': role.id,
            'user_id': self.env.user.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.SudoAssignment.create({
                'project_id': project.id,
                'role_id': role.id,
                'user_id': self.env.user.id,
            })

    def test_3(self):
        project = self.SudoProject.create({
            'name': 'Project #3',
        })
        role = self.SudoRole.create({
            'name': 'Role #3',
        })

        with mock.patch(
            _project_role_class + '.can_assign',
            return_value=False,
        ):
            with self.assertRaises(ValidationError):
                self.SudoAssignment.create({
                    'project_id': project.id,
                    'role_id': role.id,
                    'user_id': self.env.user.id,
                })

    def test_4(self):
        company_1 = self.SudoCompany.create({
            'name': 'Company #4-1',
        })
        self.SudoRole.create({
            'name': 'Role #4-1',
            'company_id': company_1.id,
        })
        company_2 = self.SudoCompany.create({
            'name': 'Company #4-2',
        })
        self.SudoRole.create({
            'name': 'Role #4-2',
            'company_id': company_2.id,
        })

    def test_5(self):
        self.SudoRole.create({
            'name': 'Role #5',
            'company_id': False,
        })

        with self.assertRaises(ValidationError):
            self.SudoRole.create({
                'name': 'Role #5',
            })

    def test_6(self):
        self.SudoRole.create({
            'name': 'Role #6',
        })

        with self.assertRaises(ValidationError):
            self.SudoRole.create({
                'name': 'Role #6',
                'company_id': False,
            })
