# Copyright 2015 Incaser Informatica S.L. - Sergio Teruel
# Copyright 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestProjectCaseDefault(TransactionCase):

    # Use case : Prepare some data for current test case
    def setUp(self):
        super(TestProjectCaseDefault, self).setUp()
        self.project = self.env['project.project'].create({
            'name': 'Project Test'
        })

    def test_project_new(self):
        self.assertEqual(len(self.project.type_ids), 7)
