# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "Project Task Stage Closed",
    'summary': "Make the Closed flag on Task Stages available without "
               "installing sale_service""",
    'author': 'ACSONE SA/NV,'
              'Tecnativa,'
              'Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/project",
    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'views/task_stage.xml',
    ],
}
