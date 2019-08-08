# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    'name': 'Base report excel',
    'summary': "Base module to create excel report (by excel_import_export)",
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'website': "https://github.com/oca/reporting-engine",
    'category': 'Reporting',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'excel_import_export',
    ],
    'data': [
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'development_status': 'beta',
    'maintainers': ['kittiu'],
}
