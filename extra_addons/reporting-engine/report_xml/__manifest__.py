# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).
{
    "name": "XML Reports",
    "version": "12.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/OCA/reporting-engine",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Allow to generate XML reports",
    "depends": [
        "web",
    ],
    "data": [
        "views/webclient_templates.xml",
        "views/ir_actions_views.xml",
    ],
    "demo": [
        "demo/report.xml",
    ]
}
