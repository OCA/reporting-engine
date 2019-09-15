# Copyright 2015 Antonio Espinosa
# Copyright 2015 Endika Iglesias
# Copyright 2015 Javier Espìnosa
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Recalculate",
    "version": "12.0.1.0.0",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "category": "Project",
    "depends": [
        'hr_timesheet',
    ],
    'data': [
        "views/project_project_view.xml",
        "views/project_task_view.xml",
        "views/project_task_stage_view.xml",
        "wizard/recalculate_wizard.xml",
    ],
    'installable': True,
}
