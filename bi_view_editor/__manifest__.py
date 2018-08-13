# -*- coding: utf-8 -*-
# Copyright 2015-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'BI View Editor',
    'summary': 'Graphical BI views builder for Odoo',
    'images': ['static/description/main_screenshot.png'],
    'author': 'Onestein,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'http://www.onestein.eu',
    'category': 'Reporting',
    'version': '10.0.1.0.2',
    'depends': [
        'base',
        'web'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'templates/assets_template.xml',
        'views/bve_view.xml',
    ],
    'qweb': [
        'templates/qweb_template.xml',
    ],
    'installable': True,
    'uninstall_hook': 'uninstall_hook'
}
