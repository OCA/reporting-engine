# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProjectTemplate(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.test_customer = self.env['res.partner'].create({
            'name': 'TestCustomer'})
        self.test_project = self.env['project.project'].create({
            'name': 'TestProject',
            'alias_name': 'test_alias',
            'total_planned_hours': 0.0,
            'partner_id': self.test_customer.id})
        self.env['project.task'].create({
            'name': 'TestTask',
            'project_id': self.test_project.id})

    # TEST 01: Set project to be a template and test name change
    def test_on_change_is_template(self):
        # Test when changing project to a template
        project_01 = self.test_project
        project_01.is_template = True
        project_01.on_change_is_template()
        self.assertEqual(project_01.name, 'TestProject (TEMPLATE)')

        # Test when changing template back to project
        project_01.is_template = False
        project_01.on_change_is_template()
        self.assertEqual(project_01.name, 'TestProject')

    # TEST 02: Create project from template
    def test_create_project_from_template(self):
        # Set Project Template
        project_01 = self.test_project
        project_01.is_template = True
        project_01.on_change_is_template()

        # Create new Project from Template
        project_01.create_project_from_template()
        new_project = self.env['project.project'].search([(
            'name', '=', 'TestProject (COPY)')])
        self.assertEqual(len(new_project), 1)
