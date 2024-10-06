# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "LibreOffice report",
    "summary": "Connection to lotemplate from Probesys",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "views/ir_actions_views.xml",
        "data/config_parameter.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "report_libreoffice/static/src/js/report/qwebactionmanager.esm.js"
        ]
    },
    "installable": True,
}
