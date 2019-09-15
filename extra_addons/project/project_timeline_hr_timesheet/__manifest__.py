# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Project Timeline - Timesheet',
    'summary': 'Shows the progress of tasks on the timeline view.',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/project',
    'category': 'Project Management',
    'version': '12.0.1.0.1',
    'depends': [
        'project_timeline',
        'hr_timesheet'
    ],
    'data': [
        'templates/assets.xml',
        'views/project_task_view.xml'
    ],
    'installable': True,
    'auto_install': True,
}
