# See README.rst file on addon root folder for license details

from datetime import date
from odoo import exceptions
from . import base


class TestProjectProjectBegin(base.BaseCase):
    calculation_type = 'date_begin'
    project_final_dates_one_task = {
        'date_begin': [
            # name, date_start, date
            ['pj_0', date(2015, 8, 1), date(2015, 8, 5)],
            ['pj_1', date(2015, 8, 2), date(2015, 8, 5)],
            ['pj_2', date(2015, 8, 3), date(2015, 8, 5)],
        ],
        'date_end': [
            ['pj_0', date(2015, 8, 10), date(2015, 10, 3)],
            ['pj_1', date(2015, 8, 17), date(2015, 10, 10)],
            ['pj_2', date(2015, 8, 21), date(2015, 10, 17)],
        ],
    }

    def __init__(self, methodName='runTest'):
        super(TestProjectProjectBegin, self).__init__(methodName=methodName)
        # Adapt project result to each type of test
        self.project_dates_res = {
            'no_tasks': {
                'date_begin': self.project_init_dates,
                'date_end': self.project_init_dates,
            },
            'one_task': self.project_final_dates_one_task,
            'tasks': self.project_final_dates,
        }

    def _check_start_end_dates_prepare(self, num_tasks, res):
        """
        @summary: Check _start_end_dates_prepare method
            * With no tasks: date is the same
            * With one task: date is task end date
            * With several tasks: date is latest task end date
        @param num_tasks: Number of task to create in test project
        @param res: Project dates expected
        """
        counter = 0
        for name, start, end in self.project_init_dates:
            # Create project with 'num_tasks' tasks
            project = self.project_create(num_tasks, {
                'calculation_type': self.calculation_type,
                'name': name,
                'date_start': start,
                'date': end,
                'resource_calendar_id': False,
            })
            # Set days (estimated_days and from_days to tasks)
            self.project_task_dates_set(
                project, self.task_dates[self.calculation_type][name])
            vals = project._start_end_dates_prepare()
            # Check vals
            if res:
                dates = res[self.calculation_type][counter]
                if self.calculation_type == 'date_begin':
                    # Only project date end must be changed
                    date_start = False
                    date_end = dates[2]
                else:
                    # Only project date start must be changed
                    date_start = dates[1]
                    date_end = False
                self.assertEqual(
                    vals.get('date_start', False), date_start,
                    "[%d] FAIL: date_start" % counter)
                self.assertEqual(
                    vals.get('date', False), date_end,
                    "[%d] FAIL: date" % counter)
            else:
                self.assertEqual(vals, res)
            counter += 1

    def test_start_end_dates_prepare_no_task(self):
        self._check_start_end_dates_prepare(0, {})

    def test_start_end_dates_prepare_one_task(self):
        self._check_start_end_dates_prepare(
            1, self.project_dates_res['one_task'])

    def test_start_end_dates_prepare_tasks(self):
        self._check_start_end_dates_prepare(
            self.num_tasks, self.project_dates_res['tasks'])

    #####################################################################
    # Check project_recalculate
    #   * With no tasks
    #   * With one task
    #   * With several tasks
    def _project_recalculate(self, num_tasks, res_project, res_tasks):
        """
        @summary: Check project_recalculate method
            * With no tasks
            * With one task
            * With several tasks
        @param num_tasks: Number of task to create in test project
        @param res_project: Project dates expected
        @param res_tasks: Tasks dates expected
        @result:
        """
        counter = 0
        for name, start, end in self.project_init_dates:
            # Create project with 'num_tasks' tasks
            project = self.project_create(num_tasks, {
                'calculation_type': self.calculation_type,
                'name': name,
                'date_start': start,
                'date': end,
                'resource_calendar_id': False,
            })
            # Set days (estimated_days and from_days to tasks)
            self.project_task_days_set(
                project, self.task_days[self.calculation_type])
            project.project_recalculate()
            # Check project dates
            dates = res_project[self.calculation_type][counter]
            self.assertEqual(
                project.date_start, dates[1],
                "[%d] FAIL: project date_start" % counter)
            self.assertEqual(
                project.date, dates[2],
                "[%d] FAIL: project date" % counter)
            # Check task dates
            for i in range(num_tasks):
                dates = res_tasks[self.calculation_type][name][i]
                task = project.tasks.filtered(lambda r: r.name == dates[0])
                self.assertEqual(
                    task.date_start.date(), dates[1],
                    "[%d, %d] FAIL: task date_start" % (counter, i))
                self.assertEqual(
                    task.date_end.date(), dates[2],
                    "[%d, %d] FAIL: task date_end" % (counter, i))
            counter += 1

    def test_project_recalculate_no_task(self):
        self._project_recalculate(
            0, self.project_dates_res['no_tasks'], False)

    def test_project_recalculate_one_task(self):
        self._project_recalculate(
            1, self.project_dates_res['one_task'], self.task_dates)

    def test_project_recalculate_tasks(self):
        self._project_recalculate(
            self.num_tasks, self.project_dates_res['tasks'], self.task_dates)

    def test_project_recalculate_exceptions(self):
        """
        @summary: Check exception raised when "Recalculate project"
            button is clicked
        """
        cases = (
            # name, calculation_type, date_start, date
            ('pj_0', False, False, False),
            ('pj_1', False, date(2015, 8, 1), False),
            ('pj_2', False, False, date(2015, 8, 1)),
            ('pj_3', False, date(2015, 8, 1), date(2015, 8, 1)),
            ('pj_4', 'date_begin', False, False),
            ('pj_5', 'date_begin', False, date(2015, 8, 1)),
            ('pj_6', 'date_end', False, False),
            ('pj_7', 'date_end', date(2015, 8, 1), False),
        )
        with self.assertRaises(exceptions.UserError):
            for num_tasks in [0, 1, 5]:
                for name, calculation_type, start, end in cases:
                    project = self.project_create(num_tasks, {
                        'calculation_type': calculation_type,
                        'name': name + '_%d' % num_tasks,
                        'date_start': start,
                        'date': end,
                        'resource_calendar_id': False,
                    })
                    project.project_recalculate()


class TestProjectProjectEnd(TestProjectProjectBegin):
    calculation_type = 'date_end'
