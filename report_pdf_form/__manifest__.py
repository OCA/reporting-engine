# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
{
    "name": "Report PDF Form",
    "summary": "Fill custom PDF form reports ",
    "version": "19.0.1.0.0",
    "development_status": "Beta",
    "category": "Reporting",
    "website": "https://github.com/OCA/reporting-engine",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["grindtildeath"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/report_pdf_form.xml",
    ],
    "demo": [
        "demo/report_pdf_form_demo.xml",
    ],
}
