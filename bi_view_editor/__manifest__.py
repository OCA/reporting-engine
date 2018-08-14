# Copyright 2015-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'BI View Editor',
    'summary': 'Graphical BI views builder for Odoo',
    'images': ['static/description/main_screenshot.png'],
    'author': 'Onestein,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/reporting-engine',
    'category': 'Reporting',
    'version': '11.0.1.0.0',
    'depends': [
        'base',
        'web',
        'base_sparse_field'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/rules.xml',
        'templates/assets_template.xml',
        'views/bve_view.xml',
    ],
    'qweb': [
        'static/src/xml/bi_view_editor.xml'
    ],
    'installable': True,
    'uninstall_hook': 'uninstall_hook'
}
