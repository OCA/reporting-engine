# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Report layout configuration",
    "summary": "Add possibility to easily modify the global report layout",
    "version": "14.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/OCA/reporting-engine",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["web", "base"],
    "data": [
        "views/document_layout.xml",
        "templates/assets.xml",
        "templates/report_templates.xml",
        "data/report_layout.xml",
    ],
    "application": False,
    "installable": True,
}
