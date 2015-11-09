# -*- coding: utf-8 -*-
##############################################################################
#
#    LibreOffice Report Engine, for OpenERP
#    Copyright (C) 2013 XCG Consulting (http://odoo.consulting)
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
#    Author: Anael LORIMIER <anael.lorimier@xcg-consulting.fr>
#            Vincent Lhote-Hatakeyama <vincent.lhote@xcg-consulting.fr>
#
##############################################################################
{
    'name': 'LibreOffice Report Engine',
    'description': '''
Generation of LibreOffice/OpenOffice reports using LibreOffice/OpenOffice
templates.

The py3o.template package is required; install it with:
    pip install py3o.template
''',
    'version': '2.0b2',
    'category': 'Reporting',
    'author': 'XCG Consulting',
    'website': 'http://odoo.consulting/',
    'depends': [
        'base',
        'report'
    ],
    'external_dependencies': {
        'python': ['py3o.template']
    },
    'data': [
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/py3o_template.xml',
        'views/py3o_server.xml',
        'views/ir_report.xml',

        'data/py3o.fusion.filetype.csv',
    ],
    'installable': True,
}
