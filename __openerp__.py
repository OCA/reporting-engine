# -*- coding: utf-8 -*-
{
    'name': 'LibreOffice Report Engine',
    'description': '''
Generation of LibreOffice/OpenOffice reports using LibreOffice/OpenOffice
templates.

The py3o.template package is required; install it with:
    pip install py3o.template
''',
    'version': '0.1',
    'category': 'Reporting',
    'author': 'XCG Consulting',
    'website': 'http://www.openerp-experts.com/',
    'depends': [
        'base'
    ],
    'data': [
        'ir_report.xml',
    ],
    'installable': True,
}
