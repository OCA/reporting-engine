# Copyright 2020 Creu Blanca
# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Report Qweb Encrypt",
    "summary": "Allow to encrypt qweb pdfs",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Ecosoft,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": [
        "web",
    ],
    "data": [
        "views/ir_actions_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "report_qweb_encrypt/static/src/js/report/action_manager_report.esm.js",
        ],
    },
    "external_dependencies": {
        "python": ["PyPDF2"]  # Python third party libraries required for module
    },
    "installable": True,
    "maintainers": ["kittiu"],
}
