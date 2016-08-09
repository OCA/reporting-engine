.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Excel report engine
===================

This module adds Excel export capabilities to the standard odoo reporting
engine.

Usage
=====

In order to create an Excel report you can:

- define a report of type 'xls'
- pass ``{'xls_export': 1}`` via the context to the report create method

The ``report_xls`` class contains a number of attributes and methods to
facilitate the creation XLS reports in OpenERP.

* cell types

  Supported cell types : text, number, boolean, date.

* cell styles

  The predefined cell style definitions result in a consistent
  look and feel of the OpenERP Excel reports.

* cell formulas

  Cell formulas can be easily added with the help of the ``rowcol_to_cell()``
  function which you can import from the ``utils.py`` module.

* Excel templates

  It is possible to define Excel templates which can be adapted
  by 'inherited' modules.
  Download the ``account_move_line_report_xls`` module
  from http://apps.odoo.com as example.

* XLS with multiple sheets

  Download the ``account_journal_report_xls`` module
  from http://apps.odoo.com as example.

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

* Noviat

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
