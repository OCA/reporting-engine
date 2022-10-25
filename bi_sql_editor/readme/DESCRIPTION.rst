This module extends the functionality of reporting, to support creation
of extra custom reports.
It allows user to write a custom SQL request. (Generally, admin users)

Once written, a new model is generated, and user can map the selected field
with odoo fields.
Then user ends the process, creating new menu, action and graph view.

Technically, the module create SQL View (or materialized view, if option is
checked). Materialized view duplicates datas, but request are fastest. If
materialized view is enabled, this module will create a cron task to refresh
the data).

By default, users member of 'SQL Request / User' can see all the views.
You can specify extra groups that have the right to access to a specific view.

Warning
-------

This module is intended for technician people in a company and for Odoo integrators.

It requires the user to know SQL syntax and Odoo models.

If you don't have such skills, do not try to use this module specially on a production
environment.

Use Cases
---------

this module is interesting for the following use cases

* You want to realize technical SQL requests, that Odoo framework doesn't allow
  (For exemple, UNION with many SELECT) A typical use case is if you want to have
  Sale Orders and PoS Orders datas in a same table

* You want to customize an Odoo report, removing some useless fields and adding
  some custom ones. In that case, you can simply select the fields of the original
  report (sale.report model for exemple), and add your custom fields

* You have a lot of data, and classical SQL Views have very bad performance.
  In that case, MATERIALIZED VIEW will be a good solution to reduce display duration
