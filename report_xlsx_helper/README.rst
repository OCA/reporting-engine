.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========================
Excel report engine helpers
===========================

This module provides a set of tools to facilitate the creation of excel reports with format xlsx.

Usage
=====

In order to create an Excel report you can define a report of type 'xlsx' in a static or dynamic way:

* Static syntax: cf. ``account_move_line_report_xls`` for an example.
* Dynamic syntax: cf. ``report_xlsx_helper_demo`` for an example

The ``AbstractReportXlsx`` class contains a number of attributes and methods to
facilitate the creation excel reports in Odoo.

* Cell types

  string, number, boolean, datetime.

* Cell formats

  The predefined cell formats result in a consistent
  look and feel of the Odoo Excel reports.

* Cell formulas

  Cell formulas can be easily added with the help of the ``_rowcol_to_cell()`` method.

* Excel templates

  It is possible to define Excel templates which can be adapted
  by 'inherited' modules.
  Download the ``account_move_line_report_xls`` module
  from http://apps.odoo.com as example.

* Excel with multiple sheets

  Download the ``account_asset_management_xls`` module
  from http://apps.odoo.com as example.

Installation
============

This module requires report_xlsx version 11.0.1.0.3 or higher.

Configuration and Usage
=======================

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/11.0

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

* Luc De Meyer <luc.demeyer@noviat.com>

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
