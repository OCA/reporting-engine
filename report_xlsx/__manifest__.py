# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base report xlsx",
    "summary": "Base module to create xlsx report",
    "author": "ACSONE SA/NV," "Creu Blanca," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "14.0.1.0.8",
    "development_status": "Mature",
    "license": "AGPL-3",
    "depends": ["base", "web"],
    "external_dependencies": {
        "python": ["xlsxwriter"],
        "deb": ["libreoffice"],
    },
    "data": ["views/webclient_templates.xml", "views/ir_actions_report.xml"],
    "demo": ["demo/report.xml"],
    "installable": True,
}
