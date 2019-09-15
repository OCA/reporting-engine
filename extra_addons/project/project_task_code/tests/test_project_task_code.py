# Copyright 2016 Tecnativa <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestProjectTaskCode(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.project_task_model = self.env['project.task']
        self.ir_sequence_model = self.env['ir.sequence']
        self.task_sequence = self.env.ref('project_task_code.sequence_task')
        self.project_task = self.env.ref('project.project_task_1')

    def test_old_task_code_assign(self):
        project_tasks = self.project_task_model.search([])
        for project_task in project_tasks:
            self.assertNotEqual(project_task.code, '/')

    def test_new_task_code_assign(self):
        number_next = self.task_sequence.number_next_actual
        code = self.task_sequence.get_next_char(number_next)
        project_task = self.project_task_model.create({
            'name': 'Testing task code',
        })
        self.assertNotEqual(project_task.code, '/')
        self.assertEqual(project_task.code, code)

    def test_copy_task_code_assign(self):
        number_next = self.task_sequence.number_next_actual
        code = self.task_sequence.get_next_char(number_next)
        project_task_copy = self.project_task.copy()
        self.assertNotEqual(project_task_copy.code, self.project_task.code)
        self.assertEqual(project_task_copy.code, code)

    def test_name_get(self):
        number_next = self.task_sequence.number_next_actual
        code = self.task_sequence.get_next_char(number_next)
        project_task = self.project_task_model.create({
            'name': 'Task Testing Get Name',
        })
        result = project_task.name_get()
        self.assertEqual(result[0][1], '[%s] Task Testing Get Name' % code)
