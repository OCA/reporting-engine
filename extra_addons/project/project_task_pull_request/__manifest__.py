# Copyright 2017 Specialty Medical Drugstore
# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Project Task Pull Request",
    "summary": "Adds a field for a PR URI to project tasks",
    "version": "12.0.1.0.0",
    "category": "Project Management",
    "website": "https://github.com/OCA/project",
    "author": "SMDrugstore, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "project",
    ],
    "data": [
        "views/project_task_pull_request_view.xml",
    ],
}
