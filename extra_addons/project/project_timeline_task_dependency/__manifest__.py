# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Project Timeline Task Dependencies',
    'summary': 'Render arrows between dependencies.',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/oca/project',
    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'depends': [
        'project_timeline',
        'project_task_dependency'
    ],
    'data': [
        'views/project_task_view.xml'
    ],
    'installable': True,
    'auto_install': True
}
