# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Excel report engine',
    'version': '0.6',
    'license': 'AGPL-3',
    'author': 'Noviat',
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
    'active': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
