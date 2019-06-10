This module is intended as a base engine for other modules to use it, so no direct result if you are a user.

If you are a developer
~~~~~~~~~~~~~~~~~~~~~~

To learn from an example, just check the `sample module`_.

To develop with this module, you need to:

* Create a module.
* Make it depend on this one.
* Follow `instructions to create reports`_ having in mind that the
  ``report_type`` field in your ``ir.actions.report.xml`` record must be
  ``qweb-xml``.

In case you want to create a `custom report`_, the instructions remain the same
as for HTML reports, and the method that you must override is also called
``_get_report_values``, even when this time you are creating a XML report.

You can make your custom report inherit ``report_xml.xsd_checked_report``, name
it like your XML ``<template>`` id prepended by ``report.``, add a ``xsd()``
method that returns a XSD in a string, and have XSD automatic checking for
free.

You can visit ``http://<server-address>/report/xml/<module.report_name>/<ids>``
to see your XML report online as a web page.

For further information, please visit:

* https://www.odoo.com/forum/help-1
* https://github.com/OCA/reporting-engine

.. _custom report: https://www.odoo.com/documentation/12.0/reference/reports.html#custom-reports
.. _instructions to create reports: https://www.odoo.com/documentation/12.0/reference/reports.html
.. _sample module: https://github.com/OCA/reporting-engine/tree/12.0/report_xml_sample
