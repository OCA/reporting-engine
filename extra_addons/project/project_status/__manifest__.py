{
    'name': "Project Status",

    'summary': """
        Project Status""",

    'author': "Patrick Wilson, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/project",

    'category': 'Project Management',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        'views/project_status.xml',
        'views/project.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
    ],

    'application': False,
    'development_status': 'Beta',
    'maintainers': ['patrickrwilson'],
}
