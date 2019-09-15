# See README.rst file on addon root folder for license details

from datetime import date, datetime
from odoo import fields
from odoo.tests.common import TransactionCase


class BaseCase(TransactionCase):
    calculation_type = 'date_begin'
    project_init_dates = [
        # name, start_date, end date
        ['pj_0', date(2015, 8, 1), date(2015, 10, 3)],  # Saturday - Saturday
        ['pj_1', date(2015, 8, 2), date(2015, 10, 10)],  # Sunday - Saturday
        ['pj_2', date(2015, 8, 3), date(2015, 10, 17)],  # Monday - Saturday
    ]
    task_days = {
        'date_begin': [
            # name, from_days, estimate_days
            ['task_0', -2, 5],      # 2015-07-30 to 2015-08-05
            ['task_1', 0, 1],       # 2015-08-03 to 2015-08-03
            ['task_2', 5, 11],      # 2015-08-07 to 2015-08-21
            ['task_3', 12, 20],     # 2015-08-18 to 2015-09-14
            ['task_4', 21, 2],      # 2015-08-31 to 2015-09-01
        ],
        'date_end': [
            # name, from_days, estimate_days
            ['task_0', 40, 5],      # 2015-08-10 to 2015-08-14
            ['task_1', 35, 11],     # 2015-08-17 to 2015-08-31
            ['task_2', 22, 20],     # 2015-09-03 to 2015-09-30
            ['task_3', 0, 1],       # 2015-10-02 to 2015-10-02
            ['task_4', -1, 2],      # 2015-10-05 to 2015-10-06
        ],
    }
    project_final_dates = {
        'date_begin': [
            ['pj_0', date(2015, 8, 1), date(2015, 9, 14)],
            ['pj_1', date(2015, 8, 2), date(2015, 9, 14)],
            ['pj_2', date(2015, 8, 3), date(2015, 9, 15)],
        ],
        'date_end': [
            ['pj_0', date(2015, 8, 10), date(2015, 10, 3)],
            ['pj_1', date(2015, 8, 17), date(2015, 10, 10)],
            ['pj_2', date(2015, 8, 21), date(2015, 10, 17)],
        ],
    }
    task_dates = {
        'date_begin': {
            'pj_0': [
                # name, date_start, date_end
                ['task_0', date(2015, 7, 30), date(2015, 8, 5)],
                ['task_1', date(2015, 8, 3), date(2015, 8, 3)],
                ['task_2', date(2015, 8, 7), date(2015, 8, 21)],
                ['task_3', date(2015, 8, 18), date(2015, 9, 14)],
                ['task_4', date(2015, 8, 31), date(2015, 9, 1)],
            ],
            'pj_1': [
                ['task_0', date(2015, 7, 30), date(2015, 8, 5)],
                ['task_1', date(2015, 8, 3), date(2015, 8, 3)],
                ['task_2', date(2015, 8, 7), date(2015, 8, 21)],
                ['task_3', date(2015, 8, 18), date(2015, 9, 14)],
                ['task_4', date(2015, 8, 31), date(2015, 9, 1)],
            ],
            'pj_2': [
                ['task_0', date(2015, 7, 30), date(2015, 8, 5)],
                ['task_1', date(2015, 8, 3), date(2015, 8, 3)],
                ['task_2', date(2015, 8, 10), date(2015, 8, 24)],
                ['task_3', date(2015, 8, 19), date(2015, 9, 15)],
                ['task_4', date(2015, 9, 1), date(2015, 9, 2)],
            ],
        },
        'date_end': {
            'pj_0': [
                ['task_0', date(2015, 8, 10), date(2015, 8, 14)],
                ['task_1', date(2015, 8, 17), date(2015, 8, 31)],
                ['task_2', date(2015, 9, 3), date(2015, 9, 30)],
                ['task_3', date(2015, 10, 2), date(2015, 10, 2)],
                ['task_4', date(2015, 10, 5), date(2015, 10, 6)],
            ],
            'pj_1': [
                ['task_0', date(2015, 8, 17), date(2015, 8, 21)],
                ['task_1', date(2015, 8, 24), date(2015, 9, 7)],
                ['task_2', date(2015, 9, 10), date(2015, 10, 7)],
                ['task_3', date(2015, 10, 9), date(2015, 10, 9)],
                ['task_4', date(2015, 10, 13), date(2015, 10, 14)],
            ],
            'pj_2': [
                ['task_0', date(2015, 8, 21), date(2015, 8, 27)],
                ['task_1', date(2015, 8, 28), date(2015, 9, 11)],
                ['task_2', date(2015, 9, 16), date(2015, 10, 14)],
                ['task_3', date(2015, 10, 16), date(2015, 10, 16)],
                ['task_4', date(2015, 10, 19), date(2015, 10, 20)],
            ],
        },
    }

    def __init__(self, methodName='runTest'):
        super(BaseCase, self).__init__(methodName=methodName)
        self.num_projects = len(self.project_init_dates)
        self.num_tasks = len(self.task_days[self.calculation_type])

    # Use case : Prepare some data for current test case
    def setUp(self):
        super(BaseCase, self).setUp()
        # Define working calendar and leaves
        m_calendar = self.env['resource.calendar']
        m_attendance = self.env['resource.calendar.attendance']
        m_leaves = self.env['resource.calendar.leaves']
        m_resource = self.env['resource.resource']
        # Working calendar
        calendar = m_calendar.create({
            'name': 'Test calendar',
        })
        # Working days
        #   - L-V 8:00 to 18:00
        days = (
            # name, dayofweek, hour_from, hour_to
            ('Monday', '0', 8, 16),
            ('Tuesday', '1', 8, 16),
            ('Wednesday', '2', 8, 16),
            ('Tuesday', '3', 8, 16),
            ('Friday', '4', 8, 16),
        )
        for day in days:
            m_attendance.create({
                'calendar_id': calendar.id,
                'name': day[0],
                'dayofweek': day[1],
                'hour_from': day[2],
                'hour_to': day[3],
            })
        # Common leaves:
        #   - 15/08/2015: 15 Agosto
        #   - 12/10/2015: 12 Octubre
        leaves = (
            # name, date_from, date_to
            ('15 Agosto', date(2015, 8, 15),
             datetime.combine(date(2015, 8, 15), datetime.max.time())),
            ('12 Octubre', date(2015, 10, 12),
             datetime.combine(date(2015, 10, 12), datetime.max.time())),
        )
        for leave in leaves:
            m_leaves.create({
                'calendar_id': calendar.id,
                'name': leave[0],
                'date_from': leave[1],
                'date_to': leave[2],
            })
        # Assign working calendar to current user resource
        resource = m_resource.search([('user_id', '=', self.uid)], limit=1)
        if not resource:
            resource = m_resource.create({
                'name': 'Test resource',
                'resource_type': 'user',
                'time_efficiency': 1.0,
                'user_id': self.uid,
                'calendar_id': calendar.id,
            })
        else:
            resource.write({
                'time_efficiency': 1.0,
                'calendar_id': calendar.id,
            })

    # Use case : Clean data after current test case
    def tearDown(self):
        # Clean data here ...
        super(BaseCase, self).tearDown()

    def project_task_add(self, project, vals=None):
        vals = vals or {}
        vals.update({
            'project_id': project.id if project else False,
            'user_id': self.uid,
        })
        return self.env['project.task'].create(vals)

    def project_task_days_set(self, project, days):
        if project.tasks:
            for day in days:
                task = project.tasks.filtered(lambda r: r.name == day[0])
                if task:
                    task.write({
                        'from_days': day[1],
                        'estimated_days': day[2],
                    })

    def project_task_dates_set(self, project, days):
        if project.tasks:
            for day in days:
                task = project.tasks.filtered(lambda r: r.name == day[0])
                if task:
                    task.write({
                        'date_start': fields.Datetime.to_datetime(day[1]),
                        'date_end': fields.Datetime.to_datetime(day[2]),
                    })

    def project_create(self, num_tasks=0, vals=None):
        vals = vals or {}
        project = self.env['project.project'].create(vals)
        self.env['project.task.type'].create({
            'name': 'Test stage',
            'include_in_recalculate': True,
            'project_ids': [(4, project.id)],
        })
        if num_tasks > 0:
            for n in range(num_tasks):
                self.project_task_add(project, {
                    'name': 'task_%d' % n,
                })
        return project
