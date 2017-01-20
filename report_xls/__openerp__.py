# -*- encoding: utf-8 -*-
# Copyright 2014 Noviat nv/sa (<http://www.noviat.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Excel report engine',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': "Noviat,Odoo Community Association (OCA)",
    'website': 'http://www.noviat.com',
    'category': 'Reporting',
    'description': """
Excel report engine
===================

This module adds Excel export capabilities to the standard odoo reporting
engine.

Report development
''''''''''''''''''
In order to create an Excel report you can\n
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

Development assistance
''''''''''''''''''''''
Contact info@noviat.com for help with the development of
Excel reports in odoo.

    """,
    'depends': ['base'],
    'external_dependencies': {'python': ['xlwt']},
    'active': False,
    'installable': True,
}
