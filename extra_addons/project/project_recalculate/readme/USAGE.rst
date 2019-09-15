There are two calculation modes:

* **Date begin**: Task start/end dates are recalculated from project's date begin
* **Date end**: Task start/end dates are recalculated from project's date end

If the project start/end date is changed in the form view, then you have to
click "Recalculate project" button to recalculate all open tasks [1]
according to the new date.

[1] 'Open tasks' means tasks in a stage that are defined with
'Include in project recalculate' = True

This a typical use case:

#. Create a project and configure:
    * Calculation type, for example "Date end".
    * Expiration Date.
#. Create tasks, configuring for each one:
    * From days, in this example, days from date end when this task must start.
    * Estimation days, duration of the task in days.
#. Click at "Recalculate project" button.
#. Go to task list and see the recalculated planning.
