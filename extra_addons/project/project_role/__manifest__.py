# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Project Roles',
    'version': '12.0.1.1.1',
    'category': 'Project',
    'website': 'https://github.com/OCA/project',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Project role-based roster',
    'depends': [
        'project',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/project_role.xml',
        'views/project_assignment.xml',
        'views/project_project.xml',
        'views/project_role.xml',
        'views/res_config_settings.xml',
    ],
}
