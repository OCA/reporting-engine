This module is intended as a base engine for other modules to use it, so no direct result if you are a user.

If you are a developer
~~~~~~~~~~~~~~~~~~~~~~

To learn from an example, just check the `demo report`_ on GitHub for
the model ``res.company`` or check it in interface from companies views.

To develop with this module, you need to:

* Create a module.
* Make it depend on this one.
* Follow `instructions to create reports`_ having in mind that the
  ``report_type`` field in your ``ir.actions.report`` record must be
  ``qweb-xml``.

In case you want to create a `custom report`_, the instructions remain the same
as for HTML reports, and the method that you must override is also called
``_get_report_values``, even when this time you are creating a XML report.

You can make your custom report inherit ``report.report_xml.abstract``, name
it in such way ``report.<module.report_name>``. Also you can add a XSD file for
report validation into ``xsd_schema`` field of your report (check
`report definition`_) and have XSD automatic checking for
free.

You can customize rendering process and validation way via changing logic of
``generate_report`` and ``validate_report`` methods in your report class.

You can visit ``http://<server-address>/report/xml/<module.report_name>/<ids>``
to see your XML report online as a web page.

For further information, please visit:

* https://www.odoo.com/forum/help-1
* https://github.com/OCA/reporting-engine

.. _custom report: https://www.odoo.com/documentation/13.0/reference/reports.html#custom-reports
.. _instructions to create reports: https://www.odoo.com/documentation/13.0/reference/reports.html
.. _demo report: https://github.com/OCA/reporting-engine/blob/13.0/report_xml/demo/demo_report.xml
.. _report definition: https://github.com/OCA/reporting-engine/blob/13.0/report_xml/demo/report.xml
