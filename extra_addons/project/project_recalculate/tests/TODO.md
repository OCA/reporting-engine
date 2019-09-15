Tests TODO for project_recalculate addon
========================================

UnitTest: project.task
----------------------

* Check _estimated_days_prepare
    * estimated_days < 0: 1
    * estimated_days = 0: 1
    * estimated_days > 0: Same

* Check _resource_calendar_select

* Check _from_days_enc
* Check _from_days_dec
    * project_day is holiday
    * project_day is not holiday
    * increment = True
    * increment = False
    * from_days < 0
    * from_days = 0
    * from_days > 0

* Check _calculation_prepare

* Check _first_interval_of_day_get

* Check _calendar_schedule_days

* Check task_recalculate
    * calculation_type = 'date_begin'
    * calculation_type = 'date_end'
    * from_days = 0
    * from_days < 0
    * from_days > 0
    * estimated_days = 1
    * estimated_days = 5
    * estimated_days = 50

* Check write
    * dates changes
    * estimated_days
