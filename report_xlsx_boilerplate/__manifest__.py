# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base Report XLSX Boilerplate",
    "version": "13.0.1.0.0",
    "summary": """
        Module extending Base Report XLSX to add Boilerplate on XLSX reports.
    """,
    "category": "Reporting",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/reporting-engine",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "depends": ["report_xlsx"],
    "external_dependencies": {"python": ["xlsxwriter", "openpyxl"]},
    "installable": True,
    "application": False,
}
