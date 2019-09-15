# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Project Milestones",
    'summary': "Project Milestones",
    'author': "Patrick Wilson, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/project",
    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': ['project', 'project_stage_closed'],
    'data': [
        'views/project.xml',
        'views/project_task.xml',
        'views/project_milestone.xml',
        'security/ir.model.access.csv',
    ],
    'application': False,
    'development_status': 'Beta',
    'maintainers': ['patrickrwilson'],
}
