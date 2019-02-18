To configure this module, you need to:

* Enter Odoo in debug mode.
* To add a specific context to a report, you should go to Settings ->
  Reporting -> Reporting and look for the report you want to edit on the
  list. You will see that now they contain a new field called Context Value
  , where you will be able to add all the desired context parameters.
* Go to Settings -> Parameters -> System Parameters. On the system
  parameters list, look for report.default.context, which is a Python
  dictionary variable where you can add a context that will be common for
  all reports.

It can also be added on the developer side using::

    <record id="model_name.report_id" model="ir.actions.report">
        <field name="context">YOUR CONTEXT HERE</field>
    </record>

