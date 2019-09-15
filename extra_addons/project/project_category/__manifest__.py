# Copyright 2015 ADHOC SA (http://www.adhoc.com.ar)
# Copyright 2017 Tecnativa - Pedro M. Baeza

{
    'name': 'Project Types',
    'version': '12.0.1.0.0',
    'category': 'Project',
    'author': 'ADHOC SA,'
              'Tecnativa, '
              'Onestein, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/project',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_type_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
