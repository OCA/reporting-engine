# Copyright 2025 Hunki Enterprises BV <https://hunki-enterprises.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "WeasyPrint QWEB renderer",
    "version": "16.0.1.0.0",
    "author": "Hunki Enterprises BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Reporting",
    "summary": "Use WeasyPrint to create PDFs",
    "depends": [
        "report_qweb_custom_renderer",
        "web",
    ],
    "website": "https://github.com/OCA/reporting-engine",
    "maintainers": ["hbrunn"],
    "demo": [
        "demo/report.xml",
    ],
    "data": [
        "views/ir_actions_report.xml",
        "views/templates.xml",
        "views/report_templates.xml",
    ],
    "external_dependencies": {
        "python": ["weasyprint"],
    },
    "assets": {
        "weasyprint_report_assets": [
            ("include", "web.report_assets_common"),
        ],
    },
}
