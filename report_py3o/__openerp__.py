# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'LibreOffice Report Engine',
    'description': '''
Generation of LibreOffice/OpenOffice reports using LibreOffice/OpenOffice
templates.

The py3o.template package is required; install it with:
    pip install py3o.template
''',
    'version': '9.0.1.0.0',
    'category': 'Reporting',
    'author': 'XCG Consulting',
    'website': 'http://odoo.consulting/',
    'depends': [
        'base',
        'report'
    ],
    'external_dependencies': {
        'python': ['py3o.template',
                   'py3o.formats']
    },
    'data': [
        'security/ir.model.access.csv',

        'views/menu.xml',
        'views/py3o_template.xml',
        'views/py3o_server.xml',
        'views/ir_report.xml',
    ],
    'installable': True,
}
