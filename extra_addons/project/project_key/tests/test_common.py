# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.tests.common import TransactionCase, HttpCase


class TestCommon(TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()

        self.Project = self.env['project.project'].with_context(
            test_project_key=True)
        self.Task = self.env['project.task'].with_context(
            test_project_key=True)

        self.project_action = self.ref("project.open_view_project_all_config")
        self.task_action = self.ref("project.action_view_task")

        self.project_1 = self.Project.create({'name': 'OCA'})
        self.project_2 = self.Project.create({'name': 'Odoo', 'key': 'ODOO'})
        self.project_3 = self.Project.create({'name': 'Python'})

        self.task11 = self.Task.create({
            'name': '1',
            'project_id': self.project_1.id,
        })

        self.task12 = self.Task.create({
            'name': '2',
            'parent_id': self.task11.id,
            'project_id': self.project_1.id,
        })

        self.task21 = self.Task.create({
            'name': '3',
            'project_id': self.project_2.id,
        })

        self.task30 = self.Task.create({
            'name': '3',
        })

    def get_record_url(self, record, model, action):
        return "/web#id=%s&view_type=form&model=%s&action=%s" % (
            record.id, model, action
        )

    def get_task_url(self, task):
        return self.get_record_url(task, task._name, self.task_action)

    def get_project_url(self, project):
        return self.get_record_url(project, project._name, self.project_action)


class HttpTestCommon(HttpCase, TestCommon):
    pass
