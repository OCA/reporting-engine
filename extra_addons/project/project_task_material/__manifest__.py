# Copyright 2012 - 2013 Daniel Reis
# Copyright 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2016 - Tecnativa - Vicent Cubells
# Copyright 2017 - Tecnativa - David Vidal
# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Project Task Material",
    "summary": "Record products spent in a Task",
    "version": "12.0.1.0.0",
    "category": "Project Management",
    "author": "Daniel Reis,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "project",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_view.xml",
    ],
}
