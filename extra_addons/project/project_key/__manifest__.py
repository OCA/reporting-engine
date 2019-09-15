# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

{
    "name": "Project key",
    "summary": "Module decorates projects and tasks with Project Key",
    "category": "Project",
    "version": "12.0.1.0.0",
    "license": "LGPL-3",
    "author": "Modoolar, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/project/",
    "depends": [
        "project",
    ],
    "data": [
        "views/project_key_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}
