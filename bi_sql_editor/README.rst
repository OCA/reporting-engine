.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================================================
BI Views builder, based on Materialized or Normal SQL Views
===========================================================

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

Configuration
=============

To configure this module, you need to:

* Go to Settings / Technical / Database Structure / SQL Views

* tip your SQL request

  .. figure:: /bi_sql_editor/static/description/01_sql_request.png
     :width: 800 px

* Select the group(s) that could have access to the view

  .. figure:: /bi_sql_editor/static/description/02_security_access.png
     :width: 800 px

* Click on the button 'Clean and Check Request'

* Once the sql request checked, the module analyses the column of the view,
  and propose field mapping. For each field, you can decide to create an index
  and set if it will be displayed on the pivot graph as a column, a row or a
  measure.

  .. figure:: /bi_sql_editor/static/description/03_field_mapping.png
     :width: 800 px

* Click on the button 'Create SQL View, Indexes and Models'. (this step could
  take a while, if view is materialized)

* If it's a MATERIALIZED view:

    * a cron task is created to refresh
      the view. You can so define the frequency of the refresh.
    * the size of view (and the indexes is displayed)

  .. figure:: /bi_sql_editor/static/description/04_materialized_view_setting.png
     :width: 800 px

* Finally, click on 'Create UI', to create new menu, action, graph view and
  search view.

Usage
=====

To use this module, you need to:

#. Go to 'Reporting' / 'Custom Reports'

#. Select the desired report

  .. figure:: /bi_sql_editor/static/description/05_reporting_pivot.png
     :width: 800 px

* You can switch to 'Pie' chart or 'Line Chart' as any report,

  .. figure:: /bi_sql_editor/static/description/05_reporting_pie.png
     :width: 800 px

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/8.0

Known issues / Roadmap
======================

* Add 'interval', after type (row/col/measure) field for date(time) fields.

Note
====

* If the view is materialized, the name of the action will contain the date
  and the time of it last refresh:

  .. figure:: /bi_sql_editor/static/description/06_action_datetime_name.png
     :width: 800 px

* The syntax of the sql request has the following constrains: the name of the
  selectable columns should be prefixed by `x_`

Sample:

.. code-block:: sql

    SELECT name as x_name
    FROM res_partner

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

* This module is highly inspired by the work of
    * Onestein: (http://www.onestein.nl/)
      Module: OCA/server-tools/bi_view_editor.
      Link: https://github.com/OCA/reporting-engine/tree/9.0/bi_view_editor
    * Anybox: (https://anybox.fr/)
      Module : OCA/server-tools/materialized_sql_view
      link: https://github.com/OCA/server-tools/pull/110
    * GRAP, Groupement Régional Alimentaire de Proximité: (http://www.grap.coop/)
      Module: grap/odoo-addons-misc/pos_sale_reporting
      link: https://github.com/grap/odoo-addons-misc/tree/7.0/pos_sale_reporting


Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
