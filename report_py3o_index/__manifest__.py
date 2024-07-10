# Copyright 2024 fah-mili/Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Py3o Report Engine: Update Indices (TOC, etc.)',
    'summary': 'Update indices (TOC, etc.) in Py3o reports',
    'version': '12.0.1.0.0',
    'category': 'Reporting',
    'license': 'AGPL-3',
    'author': 'Lambdao, Odoo Community Association (OCA)',
    "website": "https://github.com/OCA/reporting-engine",
    'depends': ['report_py3o'],
    'data': ["views/ir_actions_report.xml", "views/py3o_template.xml"],
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
