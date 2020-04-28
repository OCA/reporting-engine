# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kpi Dashboard Bokeh",
    "summary": """
        Create dashboards using bokeh""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine ",
    "depends": ["web_widget_bokeh_chart", "kpi_dashboard"],
    "data": ["views/webclient_templates.xml"],
    "qweb": ["static/src/xml/dashboard.xml"],
    "demo": ["demo/demo_dashboard.xml"],
}
