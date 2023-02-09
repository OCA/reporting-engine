# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kpi Dashboard",
    "summary": """
        Create Dashboards using kpis""",
    "version": "14.0.1.1.1",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["bus", "board", "base_sparse_field"],
    "qweb": ["static/src/xml/dashboard.xml"],
    "data": [
        "wizards/kpi_dashboard_menu.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "templates/assets.xml",
        "views/kpi_menu.xml",
        "views/kpi_kpi.xml",
        "views/kpi_dashboard.xml",
    ],
    "demo": ["demo/demo_dashboard.xml"],
    "maintainers": ["etobella"],
}
