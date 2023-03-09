# Copyright 2015-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "BI View Editor",
    "summary": "Graphical BI views builder for Odoo",
    "images": ["static/description/main_screenshot.png"],
    "author": "Onestein,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Productivity",
    "version": "15.0.1.0.0",
    "development_status": "Beta",
    "depends": ["web"],
    "external_dependencies": {
        "deb": ["graphviz"],
    },
    "data": [
        "security/ir.model.access.csv",
        "security/rules.xml",
        "views/bve_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bi_view_editor/static/src/css/bve.css",
            "bi_view_editor/static/src/js/bi_view_editor.js",
            "bi_view_editor/static/src/js/bi_view_editor.JoinNodeDialog.js",
            "bi_view_editor/static/src/js/bi_view_editor.ModelList.js",
            "bi_view_editor/static/src/js/bi_view_editor.FieldList.js",
        ],
        "web.assets_qweb": [
            "bi_view_editor/static/src/xml/bi_view_editor.xml",
        ],
    },
    "uninstall_hook": "uninstall_hook",
    "installable": True,
}
