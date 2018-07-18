.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg 
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
	
===========
XML Reports
===========

This module was written to extend the functionality of the reporting engine to
support XML reports and allow modules to generate them by code or by QWeb
templates.

Installation
============

To install this module, you need to:

* Install lxml_ in Odoo's ``$PYTHONPATH``.
* Install the repository `reporting-engine`_.

But this module does nothing for the end user by itself, so if you have it
installed it's probably because there is another module that depends on it.

Usage
=====

If you are a user
-----------------

You will be able to download XML reports from the *Print* menu found on form
and list views.

If you are a developer
----------------------

To learn from an example, just check the `sample module`_.

To develop with this module, you need to:

* Create a module.
* Make it depend on this one.
* Follow `instructions to create reports`_ having in mind that the
  ``report_type`` field in your ``ir.actions.report.xml`` record must be
  ``qweb-xml``.

In case you want to create a `custom report`_, the instructions remain the same
as for HTML reports, and the method that you must override is also called
``render_html``, even when this time you are creating a XML report.

You can make your custom report inherit ``report_xml.xsd_checked_report``, name
it like your XML ``<template>`` id prepended by ``report.``, add a ``xsd()``
method that returns a XSD in a string, and have XSD automatic checking for
free.

You can visit ``http://<server-address>/report/xml/<module.report_name>/<ids>``
to see your XML report online as a web page.

For further information, please visit:

* https://www.odoo.com/forum/help-1
* https://github.com/OCA/reporting-engine

Credits
=======

* Icon taken from http://commons.wikimedia.org/wiki/File:Text-xml.svg.

Contributors
------------

* Jairo Llopis <j.llopis@grupoesoc.es>
* Enric Tobella <etobella@creublanca.es>

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


.. _custom report: https://www.odoo.com/documentation/8.0/reference/reports.html#custom-reports
.. _instructions to create reports: https://www.odoo.com/documentation/8.0/reference/reports.html
.. _reporting-engine: https://github.com/OCA/reporting-engine
.. _sample module: https://github.com/OCA/reporting-engine/tree/8.0/report_xml_sample
.. _lxml: http://lxml.de/
