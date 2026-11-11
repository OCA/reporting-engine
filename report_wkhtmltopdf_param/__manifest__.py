# Copyright 2017 Avoin.Systems
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# noinspection PyStatementEffect
{
    "name": "Report Wkhtmltopdf Param",
    "version": "20.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Add wkhtmltopdf parameters to paper formats",
    "author": "Avoin.Systems, ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Technical Settings",
    "depends": ["web", "base_report_wkhtmltox"],
    "data": ["security/ir.access.csv", "views/paperformat.xml"],
    "installable": True,
    "auto_install": False,
    "application": False,
}
