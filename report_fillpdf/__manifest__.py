# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base report PDF Filler",
    "summary": """
        Base module that fills PDFs""",
    "author": "Creu Blanca," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [
            "fdfgen",
        ],
        "deb": [
            "pdftk",
        ],
    },
    "depends": [
        "base",
        "web",
    ],
    "data": [],
    "demo": [
        "demo/report.xml",
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "report_fillpdf/static/src/js/report/action_manager_report.esm.js",
        ],
    },
}
