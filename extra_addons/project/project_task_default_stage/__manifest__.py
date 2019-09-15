# Copyright 2015 Incaser Informatica S.L. - Sergio Teruel
# Copyright 2015 Incaser Informatica S.L. - Carlos Dauden
# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Project Task Default Stage',
    'summary': 'Recovery default task stage projects from v8',
    'version': '12.0.1.0.0',
    'category': 'Project',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    "website": "https://github.com/OCA/project",
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_view.xml',
        'data/project_data.xml',
    ],
    'installable': True,
}
