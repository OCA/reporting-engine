# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
{
    "name": "Custom report filenames",
    "summary": "Configure the filename to use when downloading a report",
    "version": "1.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "complexity": "normal",
    "category": "Reporting",
    "description": """
Custom report filenames
=======================

This addon allows for custom filenames for reports.

Configuration
=============

To configure this module, open the report whose filename you want to change
and fill in the `Download filename` field. This field is evaluated as jinja2
template with `objects` being a list of browse records of the records to
print, and `o` the first record.

Known issues / Roadmap
======================

 * Currently, only old-style reports (ir.actions.report.xml) are supported,
   it should be simple to add support for qweb reports.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Sébastien Beau <sebastien.beau@akretion.com>

Icon
----

Icon courtesy of http://www.picol.org/ (download_settings.svg)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
    """,
    "depends": [
        'web',
        'email_template',
    ],
    "data": [
        "view/ir_actions_report_xml.xml",
    ],
    "test": [
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': ['jinja2'],
    },
}
