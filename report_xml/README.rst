.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Qweb XML Reports
================

This module was written to extend the functionality of the reporting engine to
support XML reports and allow modules to generate them by code or by QWeb
templates.

Installation
============

To install this module, you need to:

* Install the repository `reporting-engine`_.

Configuration
=============

No manual configuration is needed.

Usage
=====

This module is technical, so its usage instructions are intended for module
developers.

To use this module, you need to:

* Create a module.
* Make it depend on this one.
* Follow `instructions to create reports`_ having in mind that the
  ``report_type`` field in your ``ir.actions.report.xml`` record must be
  ``qweb-xml``.

In case you want to create a `custom report`_, the instructions remain the same
as for HTML reports, and the method that you must override is also called
``render_html``, even when this time you are creating a XML report.

You can visit http://<server-address>/report/xml/<module.report_name>/<ids>
to see your XML report online as a web page.

For further information, please visit:

* https://www.odoo.com/forum/help-1
* https://github.com/OCA/reporting-engine

Known issues / Roadmap
======================

None

Credits
=======

* Icon taken from http://commons.wikimedia.org/wiki/File:Text-xml.svg.

Contributors
------------

* Jairo Llopis <j.llopis@grupoesoc.es>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.


.. _reporting-engine: https://github.com/OCA/reporting-engine
.. _instructions to create reports: https://www.odoo.com/documentation/8.0/reference/reports.html
.. _custom report: https://www.odoo.com/documentation/8.0/reference/reports.html#custom-reports
