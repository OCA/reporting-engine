# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Report Display Name in Footer",
    "summary": "Show document name in report footer",
    "version": "16.0.1.1.0",
    "development_status": "Alpha",
    "category": "Tools",
    "website": "https://github.com/OCA/reporting-engine",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["Shide", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web",
    ],
    "data": [
        "data/report_data.xml",
        "views/report_templates.xml",
    ],
}
