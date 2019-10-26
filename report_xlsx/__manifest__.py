# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Base report xlsx",

    'summary': """
        Base module to create xlsx report""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Reporting',
    'version': '10.0.1.1.1',
    'license': 'AGPL-3',
    'external_dependencies': {'python': ['xlsxwriter']},
    'depends': [
        'base',
        'report',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/header_footer.xml',
        'views/ir_report.xml',
    ],
    'installable': True,
}
