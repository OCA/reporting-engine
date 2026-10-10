# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Report Builder",
    "summary": """Allow to generate dynamic reports easily in Odoo""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": [
        "board",
        "date_range",
        "report_xlsx",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/report_instance.xml",
        "views/report_instance_column.xml",
        "views/report_template.xml",
        "views/report_template_kpi.xml",
        "views/report_style.xml",
        "reports/report_instance_reports.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "report_builder/static/src/components/**/*.esm.js",
            "report_builder/static/src/components/**/*.xml",
            "report_builder/static/src/components/**/*.scss",
        ],
        "web.report_assets_common": [
            "report_builder/static/src/scss/report_styles.scss",
        ],
        "web.assets_unit_tests": [
            "report_builder/static/tests/**/*.test.js",
        ],
    },
    "maintainers": ["etobella"],
}
