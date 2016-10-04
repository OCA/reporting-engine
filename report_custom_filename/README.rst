Custom report filenames
=======================

This addon allows for custom filenames for reports.

Configuration
=============

To configure this module, open the report whose filename you want to change and fill in the `Download filename` field. This field is evaluated as jinja2 template with `objects` being a list of browse records of the records to print, and `o` the first record. If your model contains a name field, you might write something like `${o.name}_report.pdf` as filename.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/reporting-engine/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/reporting-engine/issues/new?body=module:%20report_custom_filename%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/143/8.0

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
