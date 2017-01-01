.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Qweb Text Reports
=================

This module extends the possibilities of the native Qweb reporting engine to be able to generate any kind of text files (TXT, CSV, ZPL, EPL, ...).

Usage
=====

To add a text report, you should develop an Odoo module that contains:

* a Qweb template,
* a Qweb report definition with *report_type = qweb-txt*.

This module provides a small demo report on *Users* called *CSV List*.

The module *purchase_dilicom_csv* available on the `dilicom Github repository <https://github.com/akretion/dilicom>`_ (branch *10.0*) is a better example: it adds a report *Dilicom CSV Order* on purchase orders. This report is a CSV file with one line per order line and 2 columns: EAN13 and order quantity.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

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
