# Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'BI View Editor',
    'summary': 'Graphical BI views builder for Odoo',
    'images': ['static/description/main_screenshot.png'],
    'author': 'Onestein,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/reporting-engine',
    'category': 'Reporting',
    'version': '12.0.1.0.0',
    'development_status': 'Beta',
    'depends': [
        'web',
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
    'post_load': 'post_load',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
}
