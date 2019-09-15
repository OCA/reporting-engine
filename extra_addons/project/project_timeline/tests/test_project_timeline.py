# Copyright 2018 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import fields


class TestProjectTimeline(TransactionCase):

    def test_date_end_doesnt_unset(self):
        stage_id = self.ref('project.project_stage_2')
        task = self.env['project.task'].create({
            'name': '1',
            'date_start': '2018-05-01 00:00:00',
            'date_end': '2018-05-07 00:00:00'
        })
        task.write({
            'stage_id': stage_id,
            'date_end': '2018-10-07 00:00:00'
        })
        self.assertEqual(task.date_end,
                         fields.Datetime.from_string('2018-10-07 00:00:00'))
