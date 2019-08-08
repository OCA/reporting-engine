# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    'name': 'Demo for Base report excel',
    'author': 'Ecosoft,Odoo Community Association (OCA)',
    'website': "https://github.com/oca/reporting-engine",
    'category': 'Reporting',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'sale_management',
        'report_excel',
    ],
    'data': [
        'report/sale_order/report.xml',
        'report/sale_order/templates.xml',
        'report/partner_list/report.xml',
        'report/partner_list/templates.xml',
        'report/partner_list/report_partner_list.xml',
    ],
    'installable': True,
    'development_status': 'beta',
    'maintainers': ['kittiu'],
}
