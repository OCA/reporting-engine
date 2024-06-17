# Copyright (C) 2015 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "SQL Export",
    "version": "16.0.2.2.0",
    "author": "Akretion,GRAP,Odoo Community Association (OCA)",
    "maintainers": ["legalsylvain"],
    "website": "https://github.com/OCA/reporting-engine",
    "license": "AGPL-3",
    "category": "Generic Modules/Others",
    "summary": "Export data in csv file with SQL requests",
    "depends": [
        "spreadsheet_dashboard",
        "sql_request_abstract",
    ],
    "data": [
        "views/sql_export_view.xml",
        "wizard/wizard_file_view.xml",
        "security/sql_export_security.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        "demo/sql_export.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "sql_export/static/src/scss/modal_properties.scss",
        ]
    },
    "installable": True,
}
