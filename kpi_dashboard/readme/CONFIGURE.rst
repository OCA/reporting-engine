Configure KPIs
~~~~~~~~~~~~~~

#. Access `Dashboards > Configuration > KPI Dashboards > Configure KPI`
#. Create a new KPI specifying the computation method and the kpi type

   #. Number: result must contain a `value` and, if needed, a `previous`
   #. Meter: result must contain `value`, `min` and `max`
   #. Graph: result must contain a list on `graphs` containing `values`, `title` and `key`

#. In order to compute the KPI you can use a predefined function from a model or
   use the code to directly compute it.

Using KPI with code
~~~~~~~~~~~~~~~~~~~

Define the code directly on the code field. You can use `self` and `model` as the kpi element
The script should create a variable called `result` as a dictionary that
will be stored as the value.
For example, we can use::

    result = {}
    result['value'] = len(model.search([('id', '=', %s)]))
    result['previous'] = len(model.search([('id', '!=', %s)]))

Configure dashboards
~~~~~~~~~~~~~~~~~~~~

#. Access `Dashboards > Configuration > KPI Dashboards > Configure Dashboards`
#. Create a new dashboard and specify all the standard parameters on `Widget configuration`
#. Append elements on KPIs
#. You can preview the element using the dashboard view
#. You can create the menu entry directly using the `Generate menu` button
