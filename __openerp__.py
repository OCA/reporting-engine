# -*- coding: utf-8 -*-
{
    'name': 'LibreOffice Report Engine',
    'description': '''
Generation of LibreOffice/OpenOffice reports using LibreOffice/OpenOffice
templates.

The py3o.template package is required; install it with:
    pip install py3o.template
''',
    'version': '1.1.1',
    'category': 'Reporting',
    'author': 'XCG Consulting',
    'website': 'http://www.openerp-experts.com/',
    'depends': [
        'base'
    ],
    'external_dependencies': {
        'python': ['py3o.template', 'oe_json_serializer']
    },
    'data': [
        'menu.xml',
        'ir_report.xml',
        'py3o_template.xml',
        'py3o_server.xml',
        'data/py3o.fusion.filetype.csv',
    ],
    'installable': True,
}
