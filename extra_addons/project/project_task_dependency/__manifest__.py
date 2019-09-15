# © 2016 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Project Task Dependencies',
    'version': '12.0.1.0.0',
    'category': 'Project',
    'website': 'https://github.com/OCA/project',
    'summary': 'Enables to define dependencies (other tasks) of a task',
    'author': "Onestein,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'depends': [
        'project'
    ],
    'data': [
        'views/project_task_view.xml'
    ],
    'installable': True,
    'auto_install': False,
}
