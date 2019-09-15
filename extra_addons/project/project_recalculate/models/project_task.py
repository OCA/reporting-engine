# Copyright 2015 Antonio Espinosa
# Copyright 2015 Endika Iglesias
# Copyright 2015 Javier Espìnosa
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from pytz import timezone, utc

from odoo import exceptions
from odoo import models, fields, api, _
from datetime import datetime


class ProjectTask(models.Model):
    _inherit = 'project.task'

    from_days = fields.Integer(
        string='From days',
        help='Anticipation days from date begin or date end', default=0)
    estimated_days = fields.Integer(
        string='Estimated days', help='Estimated days to end', default=1,
        oldname='anticipation_days')
    include_in_recalculate = fields.Boolean(
        related="stage_id.include_in_recalculate", readonly=True,
    )

    @api.constrains('estimated_days')
    def _estimated_days_check(self):
        for task in self:
            if task.estimated_days <= 0:
                raise exceptions.ValidationError(
                    _('Estimated days must be greater than 0.')
                )

    @api.multi
    def _update_recalculated_dates(self, vals):
        """
            Try to calculate estimated_days and from_days fields
            when date_start or date_end change.

            Dates fields (date_start, date_end) have preference to
            estimated_days and from_days
            except if context['task_recalculate'] == True, in other words,
            except if this change is done because task recalculating.
        """
        self.ensure_one()
        # If no date changes, do nothing
        if 'date_start' not in vals and 'date_end' not in vals:
            return vals
        # If we are changing dates because of task recalculating, do nothing
        if self.env.context.get('task_recalculate'):
            return vals
        to_datetime = fields.Datetime.to_datetime
        date_start = to_datetime(vals.get('date_start', self.date_start))
        date_end = to_datetime(vals.get('date_end', self.date_end))
        # If any date is False, can't calculate estimated_days nor from_days
        if not date_start or not date_end:
            return vals
        resource, calendar = self._resource_calendar_select()
        date_start = self._resource_timezone(date_start, resource)
        date_end = self._resource_timezone(date_end, resource)
        if date_end < date_start or not resource or not calendar:
            return vals
        # Calculate estimated_day
        vals['estimated_days'] = calendar.get_working_days_of_date(
            start_dt=date_start, end_dt=date_end, resource=resource)
        # Calculate from_days depending on project calculation type
        calculation_type = self.project_id.calculation_type
        if calculation_type:
            invert = False
            increment = calculation_type == 'date_begin'
            if increment:
                if not self.project_id.date_start:
                    # Can't calculate from_days without project date_start
                    return vals
                project_date = self.project_id.date_start
                date_end = date_start
                date_start = fields.Datetime.to_datetime(project_date)
            else:
                if not self.project_id.date:
                    # Can't calculate from_days without project date
                    return vals
                project_date = self.project_id.date
                date_end = fields.Datetime.to_datetime(project_date)
            date_start = self._resource_timezone(date_start, resource)
            date_end = self._resource_timezone(date_end, resource)
            if date_end < date_start:
                invert = True
                date_start, date_end = date_end, date_start
            from_days = calendar.get_working_days_of_date(
                start_dt=date_start, end_dt=date_end, resource=resource)
            if invert and from_days:
                from_days = from_days * (-1)
            from_days = self._from_days_enc(
                from_days, project_date, resource, calendar, increment)
            vals['from_days'] = from_days
        return vals

    def _estimated_days_prepare(self, vals):
        # estimated_days must be greater than zero, if not defaults to 1
        if 'estimated_days' in vals and vals['estimated_days'] < 1:
            vals['estimated_days'] = 1
        return vals

    def _resource_calendar_select(self):
        """
            Select working calendar and resource related this task:
            Working calendar priority:
                - project
                - user
                - company
        """
        self.ensure_one()
        resource = False
        if self.user_id:
            # Get first resource of assigned user
            resource = self.env['resource.resource'].search(
                [('user_id', '=', self.user_id.id)], limit=1)
        if resource and resource.calendar_id:
            # Get calendar from project
            calendar = resource.calendar_id
        elif self.project_id.resource_calendar_id:
            # Get calendar from assigned user
            calendar = self.project_id.resource_calendar_id
        else:
            # Get calendar from company
            if self.user_id.company_id:
                # Get company from assigned user
                company = self.user_id.company_id
            else:
                # If not assigned user, get company from current user
                company = self.env.user.company_id
            calendar = self.env['resource.calendar'].search(
                [('company_id', '=', company.id)], limit=1)
        return resource, calendar

    def _from_days_enc(self, from_days, project_date,
                       resource=None, calendar=None, increment=True):
        interval = self._first_interval_of_day_get(
            project_date, resource=resource, calendar=calendar)
        # If project_date is holidays
        if not interval:
            if from_days > 0 and increment:
                from_days += 1
            elif from_days < 0 and not increment:
                from_days -= 1
            elif from_days == 0:
                from_days = 1 if increment else -1
        return from_days

    def _from_days_dec(self, from_days, project_date,
                       resource=None, calendar=None, increment=True):
        if from_days == 0:
            return 1 if increment else -1
        interval = self._first_interval_of_day_get(
            project_date, resource=resource, calendar=calendar)
        # If project_date is not holidays
        if interval:
            if from_days > 0:
                from_days += 1
            elif from_days < 0:
                from_days -= 1
        return from_days

    def _calculation_prepare(self):
        """
            Prepare calculation parameters:
                - Increment=True, when task date_start is after project date
                - Increment=False, when task date_start if before project date
                - project_date, reference project date
        """
        self.ensure_one()
        increment = self.project_id.calculation_type == 'date_begin'
        if increment:
            if not self.project_id.date_start:
                raise exceptions.UserError(
                    _('Start Date field must be defined.')
                )
            project_date = self.project_id.date_start
            days = self.from_days
        else:
            if not self.project_id.date:
                raise exceptions.UserError(
                    _('End Date field must be defined.')
                )
            project_date = self.project_id.date
            days = self.from_days * (-1)
        return increment, project_date, days

    def _resource_timezone(self, dt, resource=None, calendar=None):
        result = dt
        if not dt.tzinfo:
            if resource or calendar:
                tz = timezone((resource or calendar).tz)
            else:
                tz = utc
            result = tz.localize(dt)
        return result

    def _get_work_intervals(self, day_date, resource=None, calendar=None):
        start_dt = datetime.combine(day_date, datetime.min.time())
        end_dt = datetime.combine(day_date, datetime.max.time())
        start_dt = self._resource_timezone(start_dt, resource)
        end_dt = self._resource_timezone(end_dt, resource)
        if not calendar:
            intervals = self._interval_default_get()
            intervals -= self._leave_intervals(start_dt, end_dt, resource)
        else:
            intervals = calendar._work_intervals(start_dt, end_dt, resource)

        return intervals

    def _first_interval_of_day_get(self, day_date, resource=None,
                                   calendar=None):
        intervals = self._get_work_intervals(day_date, resource, calendar)
        return (list(intervals)[:1] or [False])[0]

    def _last_interval_of_day_get(self, day_date, resource=None,
                                  calendar=None):
        intervals = self._get_work_intervals(day_date, resource, calendar)
        return (list(intervals)[-1:] or [False])[0]

    def _calendar_plan_days(self, days, day_date, resource=None,
                            calendar=None):
        if not day_date:
            return False
        # date to datetime
        if days >= 0:
            day_dt = datetime.combine(day_date, datetime.min.time())
        else:
            day_dt = datetime.combine(day_date, datetime.max.time())
        day_dt = self._resource_timezone(day_dt, resource)
        planned_dt = calendar.plan_days_to_resource(
            days, day_dt, compute_leaves=True, resource=resource)

        return planned_dt or False

    @api.multi
    def task_recalculate(self):
        """Recalculate task start date and end date depending on
        project calculation_type, estimated_days and from_days.
        """
        for task in self.filtered('include_in_recalculate'):
            resource, calendar = task._resource_calendar_select()
            if not calendar:
                continue
            increment, project_date, from_days = task._calculation_prepare()
            date_start = False
            date_end = False
            from_days = self._from_days_dec(
                from_days, project_date, resource, calendar, increment)
            planned_dt = self._calendar_plan_days(
                from_days, project_date, resource, calendar)
            if planned_dt:
                day = planned_dt.replace(hour=0, minute=0, second=0)
                first = self._first_interval_of_day_get(
                    day, resource, calendar)
                if first:
                    date_start = first[0]
            if date_start:
                end_planned_dt = self._calendar_plan_days(
                    task.estimated_days, date_start, resource, calendar)
                if end_planned_dt:
                    date_end = self._last_interval_of_day_get(
                        end_planned_dt, resource, calendar)[1]
            if date_start:
                date_start = date_start.astimezone(utc)
            if date_end:
                date_end = date_end.astimezone(utc)

            task.with_context(task.env.context, task_recalculate=True).write({
                'date_start': date_start or False,
                'date_end': date_end or False,
                'date_deadline': date_end or False,
            })
        return True

    @api.multi
    def write(self, vals):
        for this in self:
            vals = this._update_recalculated_dates(vals)
            vals = this._estimated_days_prepare(vals)
            super(ProjectTask, this).write(vals)
        return True
