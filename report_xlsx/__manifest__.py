# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base report xlsx",
    "summary": "Base module to create xlsx report",
    "author": "ACSONE SA/NV," "Creu Blanca," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "13.0.1.1.1",
    "development_status": "Production/Stable",
    "license": "AGPL-3",
    "depends": ["base", "web"],
    "external_dependencies": {"python": ["openpyxl"]},
    "data": ["views/webclient_templates.xml"],
    "demo": ["demo/report.xml"],
    "installable": True,
}
