# Copyright 2014 Daniel Reis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Add State field to Project Stages',
    'version': '12.0.1.0.0',
    'category': 'Project Management',
    'summary': 'Restore State attribute removed from Project Stages in 8.0',
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/project',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_view.xml',
    ],
}
