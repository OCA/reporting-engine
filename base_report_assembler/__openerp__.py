# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{'name': 'Base Report Assembler',
 'version': '1.0',
 'category': 'Report',
 'description': """
Base Report Assembler
=====================

Defines a new type of report which is an assemblage of multiple other reports
of the same object.

For example you can merge the pdf output of a rml invoice report with the pdf
output of a webkit payment slip.

To install this assemblage option for specific object you can install
the folling module(s):

- Invoices: invoice_report_assemble (lp:account-invoice-report)

""",
 'author': "Camptocamp,Odoo Community Association (OCA)",
 'maintainer': 'Camptocamp',
 'website': 'http://www.camptocamp.com/',
 'depends': ['base'],
 'data': [],
 'test': [],
 'installable': False,
 'auto_install': False,
 'application': False,
 }
