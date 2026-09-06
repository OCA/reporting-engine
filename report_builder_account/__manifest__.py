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
        "account",
        "report_builder",
    ],
    "data": [
        "data/report.template.kpi.query.kind.csv",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "maintainers": ["etobella"],
}
