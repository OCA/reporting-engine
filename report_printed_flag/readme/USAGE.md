For End Users
=============

1. Install ``report_printed_flag`` module
2. Install extension modules that support printed flags (e.g., ``report_printed_flag_account``)
3. Go to *Settings > Reporting > Printed Flag > Configurations*
4. Create a configuration for your model (Company + Model)
5. Add report rules (select report + optional domain condition)
6. Generate a configured report from a document (e.g., print an invoice)

Result:

- The ``printed`` field is automatically set to ``True``
- A log entry is created (if enabled in configuration)
- Printed report names are computed (if enabled in configuration)

Access logs via:

*Settings > Reporting > Printed Flag > Logs*

For Module Developers
=====================

To add printed flag support to a custom model:

1. Create your model inheriting from ``report.printed.mixin``:


    class MyModel(models.Model):
        _name = 'my.model'
        _inherit = ['my.model', 'report.printed.mixin']

2. Create QWeb PDF reports for your model (standard Odoo process)

3. Instruct users to configure which reports trigger the printed flag via the UI

That's it! The mixin provides all field and method implementations automatically.

Optional: Add UI Elements
--------------------------

You may optionally add buttons to your views to open the logs:

    <button name="action_view_printed_logs"
            type="object"
            string="View Printed Logs"
            icon="fa-print"
            invisible="not printed_report_names"/>
