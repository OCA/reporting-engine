# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base report PDF Filler",
    "summary": """
        Base module that fills PDFs""",
    "author": "Creu Blanca," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "14.0.1.0.1",
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
    "data": [
        "views/webclient_templates.xml",
    ],
    "demo": [
        "demo/report.xml",
    ],
    "installable": True,
}
