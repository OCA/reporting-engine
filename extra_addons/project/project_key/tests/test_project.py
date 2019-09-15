# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from .test_common import TestCommon


class TestProject(TestCommon):

    def test_01_key(self):
        self.assertEqual(self.project_1.key, "OCA")
        self.assertEqual(self.project_2.key, "ODOO")
        self.assertEqual(self.project_3.key, "PYT")

    def test_02_change_key(self):
        self.project_1.key = "XXX"

        self.assertEqual(self.task11.key, "XXX-1")
        self.assertEqual(self.task12.key, "XXX-2")

    def test_03_name_search(self):

        projects = self.Project.name_search('ODO')
        self.assertEqual(len(projects), 1)

        non_odoo_projects = [
            x[0] for x in self.Project.name_search("ODO", operator="not ilike")
        ]

        odoo_projects = self.Project.browse(non_odoo_projects).filtered(
            lambda x: x.id == self.project_2.id
        )

        self.assertEqual(len(odoo_projects), 0)

    def test_04_name_search_empty(self):
        projects = self.Project.name_search('')
        self.assertGreater(len(projects), 0)

    def test_05_name_onchange(self):
        project = self.Project.new({'name': 'Software Development'})
        project._onchange_project_name()
        self.assertEqual(project.key, 'SD')

    def test_06_name_onchange(self):
        project = self.Project.new({})
        project._onchange_project_name()
        self.assertEqual(project.key, '')

    def test_07_delete(self):
        self.project_1.task_ids.unlink()
        self.project_1.unlink()

        self.project_2.task_ids.unlink()
        self.project_2.unlink()

        self.project_3.unlink()

    def test_08_generate_empty_project_key(self):
        empty_key = self.Project.generate_project_key(False)
        self.assertEqual(empty_key, '')

    def test_09_name_onchange_with_key(self):
        project = self.Project.new({
            'name': 'Software Development',
            'key': 'TEST',
        })
        project._onchange_project_name()
        self.assertEqual(project.key, 'TEST')
