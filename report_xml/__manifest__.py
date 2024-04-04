# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).
{
    "name": "XML Reports",
    "version": "16.0.1.1.2",
    "category": "Reporting",
    "website": "https://github.com/OCA/reporting-engine",
    "development_status": "Production/Stable",
    "author": "Tecnativa, Odoo Community Association (OCA), Avoin.Systems",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Allow to generate XML reports",
    "depends": ["web"],
    "data": [
        "views/ir_actions_report_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "report_xml/static/src/js/report/action_manager_report.esm.js",
        ],
    },
    "demo": [
        "demo/report.xml",  # register report in the system
        "demo/demo_report.xml",  # report body definition
    ],
    "post_init_hook": "post_init_hook",
}
