This module extends the field `priority` in project tasks, adding two new levels of priority.
The two new levels of priority are: `High` and `Very High`.


On a task form, the priority widget is displayed with three stars instead of one:

.. figure:: https://raw.githubusercontent.com/OCA/project/12.0/project_task_add_very_high/static/description/image.png
   :alt: On form, priority widget shows three stars instead of one


On a Kanban view, the priority widget is displayed as well with three stars instead of one:

.. figure:: https://raw.githubusercontent.com/OCA/project/12.0/project_task_add_very_high/static/description/image2.png
   :alt: On kanban, priority widget shows three stars instead of one


Without having this module installed, on the form it would look like as that:

.. figure:: https://raw.githubusercontent.com/OCA/project/12.0/project_task_add_very_high/static/description/image_a.png
   :alt: On form, priority widget shows one star

and on Kanban:

.. figure:: https://raw.githubusercontent.com/OCA/project/12.0/project_task_add_very_high/static/description/image2_a.png
   :alt: On kanban, priority widget shows one star

In case this module is uninstalled, all the tasks that were previously set as `High` or `Very High` priority will be
converted to `Normal` priority.
