import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-project",
    description="Meta package for oca-project Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-project_category',
        'odoo12-addon-project_description',
        'odoo12-addon-project_key',
        'odoo12-addon-project_milestone',
        'odoo12-addon-project_parent_task_filter',
        'odoo12-addon-project_recalculate',
        'odoo12-addon-project_role',
        'odoo12-addon-project_stage_closed',
        'odoo12-addon-project_stage_state',
        'odoo12-addon-project_status',
        'odoo12-addon-project_tag',
        'odoo12-addon-project_task_add_very_high',
        'odoo12-addon-project_task_code',
        'odoo12-addon-project_task_default_stage',
        'odoo12-addon-project_task_dependency',
        'odoo12-addon-project_task_material',
        'odoo12-addon-project_task_pull_request',
        'odoo12-addon-project_template',
        'odoo12-addon-project_template_milestone',
        'odoo12-addon-project_timeline',
        'odoo12-addon-project_timeline_hr_timesheet',
        'odoo12-addon-project_timeline_task_dependency',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
