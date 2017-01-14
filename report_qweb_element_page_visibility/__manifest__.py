# -*- coding: utf-8 -*-
# Copyright 2015 Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Report Qweb Element Page Visibility',
    'version': '10.0.1.0.0',
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'category': 'Tools',
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "application": False,
    'installable': True,
    'data': [
        'views/layouts.xml',
    ],
    'depends': [
        'report',
    ],
}
