To configure this module, you need to:

* Go to Settings / Technical / Database Structure / SQL Views

* tip your SQL request

  .. figure:: ../static/description/01_sql_request.png
     :width: 800 px

* Select the group(s) that could have access to the view

  .. figure:: ../static/description/02_security_access.png
     :width: 800 px

* Click on the button 'Clean and Check Request'

* Once the sql request checked, the module analyses the column of the view,
  and propose field mapping. For each field, you can decide to create an index
  and set if it will be displayed on the pivot graph as a column, a row or a
  measure.

  .. figure:: ../static/description/03_field_mapping.png
     :width: 800 px

* Click on the button 'Create SQL View, Indexes and Models'. (this step could
  take a while, if view is materialized)

* If it's a MATERIALIZED view:

    * a cron task is created to refresh
      the view. You can so define the frequency of the refresh.
    * the size of view (and the indexes is displayed)

  .. figure:: ../static/description/04_materialized_view_setting.png
     :width: 800 px

* Before applying the final step, you will need to add a specific Parent Menu to
  use when creating the UI Menu for the report. By default, it will be set with
  the `SQL Views` menu, which can be changed before creating the UI elements in
  order to have the report accessible from a different place within Odoo.

* Finally, click on 'Create UI', to create new menu, action, graph view and
  search view.
