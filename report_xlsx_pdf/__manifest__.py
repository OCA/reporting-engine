# Copyright 2022 Openindustry.it (<https://openindustry.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Export xlsx report to pdf",
    "summary": "Extend report_xlsx to export directly to pdf",
    "author": "Openindustry.it," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "license": "AGPL-3",
    "depends": ["report_xlsx"],
    "external_dependencies": {
        "python": ["xlsxwriter"],
        "deb": ["libreoffice"],
    },
    "data": ["views/ir_actions_report.xml"],
    "demo": ["demo/report.xml"],
    "installable": True,
}
