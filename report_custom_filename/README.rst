Custom report filenames
=======================

This addon allows for custom filenames for reports.

Configuration
=============

To configure this module, open the report whose filename you want to change and fill in the `Download filename` field. This field is evaluated as jinja2 template with `objects` being a list of browse records of the records to print, and `o` the first record.

Known issues / Roadmap
======================

 * Currently, only old-style reports (ir.actions.report.xml) are supported, it should be simple to add support for qweb reports.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/reporting-engine/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/reporting-engine/issues/new?body=module:%20report_custom_filename%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Icon
----

Icon courtesy of http://www.picol.org/ (download_settings.svg)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
