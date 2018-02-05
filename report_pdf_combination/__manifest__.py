# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "Base report pdf-combination",

    'summary': """
        Base module to to generate pdf from other pdf files""",
    'author': 'IT-Projects LLC,'
              'Odoo Community Association (OCA)',
    'website': "http://github.com/oca/reporting-engine",
    'category': 'Reporting',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'PyPDF2',
        ],
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
