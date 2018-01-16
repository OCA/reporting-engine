# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Py3o Report Engine - Fusion server support',
    'summary': 'Let the fusion server handle format conversion.',
    'version': '10.0.1.0.0',
    'category': 'Reporting',
    'license': 'AGPL-3',
    'author': 'XCG Consulting,'
              'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/reporting-engine',
    'depends': ['report_py3o'],
    'external_dependencies': {
        'python': [
            'py3o.template',
            'py3o.formats',
        ],
    },
    'demo': [
        "demo/report_py3o.xml",
    ],
    'data': [
        "views/ir_report.xml",
        'security/ir.model.access.csv',
        'views/py3o_server.xml',
    ],
    'installable': True,
}
