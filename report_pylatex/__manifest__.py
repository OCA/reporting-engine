# -*- encoding: utf-8 -*-
##############################################################################
#
#    OmniaSolutions, Open Source Management Solution    
#    Copyright (C) 2010-2011 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Pylatex Reporting connection',
    'description': """
Technical : Improve odoo reporting to also use pylatex for report generation
https://jeltef.github.io/PyLaTeX/latest/faq.html
============================================================================
    """,
    'version': '16.0.1',
    'sequence':1,
    'author': 'OmniaSolutions',
    "license": "AGPL-3",
    "summary": "pylatex Reporting",
    'website': 'http://www.omniasolutions.website',
    "category": "Reporting",
    'depends': ["base","mail"],
    'external_dependencies': {'python': ['pylatex']},
    'data': [# security
             # views
             'views/ir_report.xml',
             # wizard
             # report
             # data
     ],
    "assets": {
        "web.assets_backend": [
            "pylatex_report/static/src/js/report/action_manager_report.js"
        ],
    },
    'installable': True,
}
