# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base report csv",
    "summary": "Base module to create csv report",
    "author": "Creu Blanca, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "16.0.2.1.0",
    "license": "AGPL-3",
    "depends": ["base", "web"],
    "demo": ["demo/report.xml"],
    "data": ["views/ir_actions_views.xml"],
    "assets": {
        "web.assets_backend": [
            "report_csv/static/src/js/report/qwebactionmanager.esm.js"
        ]
    },
    "installable": True,
}
