# Copyright 2019 Patrick Wilson <patrickraymondwilson@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestProjectTemplate(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.test_customer = self.env['res.partner'].create({
            'name': 'TestCustomer'})

        # Create project with 2 milestones
        self.test_project = self.env['project.project'].create({
            'name': 'TestProject',
            'alias_name': 'test_alias',
            'total_planned_hours': 0.0,
            'partner_id': self.test_customer.id})
        self.test_milestone_1 = self.env['project.milestone'].create({
            'name': 'Test_Milestone_1',
            'project_id': self.test_project.id})
        self.test_milestone_2 = self.env['project.milestone'].create({
            'name': 'Test_Milestone_2',
            'project_id': self.test_project.id})

        # Create 2 tasks for milestone 1
        self.env['project.task'].create({
            'name': 'TestTask_1',
            'project_id': self.test_project.id,
            'milestone_id': self.test_milestone_1.id})
        self.env['project.task'].create({
            'name': 'TestTask_2',
            'project_id': self.test_project.id,
            'milestone_id': self.test_milestone_1.id})

        # Create 1 tasks for milestone 2
        self.env['project.task'].create({
            'name': 'TestTask_3',
            'project_id': self.test_project.id,
            'milestone_id': self.test_milestone_2.id})

    # TEST 01: Create project from template and verify milestones & tasks
    def test_create_project_from_template(self):
        # Set Project Template
        project_01 = self.test_project
        project_01.is_template = True
        project_01.on_change_is_template()

        # Create new Project from Template
        project_01.create_project_from_template()
        new_project = self.env['project.project'].search([(
            'name', '=', 'TestProject (COPY)')])

        # Verify that the project was created successfully
        self.assertEqual(len(new_project), 1)

        # Verify that the Milestones were created successfully
        self.assertEqual(len(new_project.milestone_ids), 2)

        # Verify that the tasks were created successfully with milestones
        task_milestone_1_ids = self.env['project.task'].search([(
            'milestone_id.name', '=', 'Test_Milestone_1'),
            ('project_id', '=', new_project.id)])
        self.assertEqual(len(task_milestone_1_ids), 2)

        task_milestone_2_ids = self.env['project.task'].search([(
            'milestone_id.name', '=', 'Test_Milestone_2'),
            ('project_id', '=', new_project.id)])
        self.assertEqual(len(task_milestone_2_ids), 1)
