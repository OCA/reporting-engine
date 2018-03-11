# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "Base report PDF Filler",

    'summary': """
        Base module that fills PDFs""",
    'author': 'Creu Blanca,'
              'Odoo Community Association (OCA)',
    'website': "http://github.com/oca/reporting-engine",
    'category': 'Reporting',
    'version': '11.0.1.0.1',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'fdfgen',
        ],
        'bin': [
            'pdftk',
        ]
    },
    'depends': [
        'base', 'web',
    ],
    'data': [
        'views/webclient_templates.xml',
    ],
    'demo': [
        'demo/report.xml',
    ],
    'installable': True,
}
