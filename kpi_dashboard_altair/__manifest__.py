# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kpi Dashboard Altair",
    "summary": """
        Create dashboards using altair""",
    "version": "12.0.1.0.3",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["kpi_dashboard"],
    "data": ["views/webclient_templates.xml"],
    "qweb": ["static/src/xml/dashboard.xml"],
    "external_dependencies": {
        "python": ["altair"],
    },
    "demo": ["demo/demo_dashboard_altair.xml"],

    "maintainers": ["etobella"],
}
