# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base report external PDF",
    "summary": """
        Base module that allows to define manual generation of PDFs""",
    "author": "Creu Blanca," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["web"],
    "data": ["views/webclient_templates.xml", "data/report.xml"],
    "demo": ["demo/report.xml"],
    "installable": True,
}
