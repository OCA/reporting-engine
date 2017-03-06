# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Py3o Report Engine',
    'summary': 'Reporting engine based on Libreoffice (ODT -> ODT, '
               'ODT -> PDF, ODT -> DOC, ODT -> DOCX, ODS -> ODS, etc.)',
    'version': '10.0.1.0.0',
    'category': 'Reporting',
    'license': 'AGPL-3',
    'author': 'XCG Consulting,'
              'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': 'http://odoo.consulting/',
    'depends': ['report'],
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
        'demo/report_py3o.xml',
    ],
    'installable': True,
}
