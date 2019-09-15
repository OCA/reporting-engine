# Copyright 2016-2017 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project timeline",
    "summary": "Timeline view for projects",
    "version": "12.0.1.2.0",
    "category": "Project Management",
    "website": "https://github.com/OCA/project",
    "author": "Tecnativa, Onestein, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "project",
        "web_timeline",
    ],
    "data": [
        "templates/assets.xml",
        "views/project_project_view.xml",
        "views/project_task_view.xml",
    ],
    "demo": [
        'demo/project_project_demo.xml',
        'demo/project_task_demo.xml',
    ]
}
