# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Kpi Dashboard",
    "summary": """Create Dashboards using kpis""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["bus", "board", "base_sparse_field"],
    "qweb": ["static/src/xml/dashboard.xml"],
    "data": [
        "wizards/kpi_dashboard_menu.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/kpi_menu.xml",
        "views/kpi_kpi.xml",
        "views/kpi_dashboard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "kpi_dashboard/static/src/js/widget_registry.js",
            "kpi_dashboard/static/src/js/widget/abstract_widget.js",
            "kpi_dashboard/static/src/js/dashboard_renderer.js",
            "kpi_dashboard/static/src/js/dashboard_model.js",
            "kpi_dashboard/static/src/js/dashboard_controller.js",
            "kpi_dashboard/static/src/js/dashboard_view.js",
            "kpi_dashboard/static/src/js/widget/integer_widget.js",
            "kpi_dashboard/static/src/js/widget/number_widget.js",
            "kpi_dashboard/static/src/js/widget/counter_widget.js",
            "kpi_dashboard/static/src/js/widget/meter_widget.js",
            "kpi_dashboard/static/src/js/widget/graph_widget.js",
            "kpi_dashboard/static/src/js/widget/text_widget.js",
            "kpi_dashboard/static/src/js/field_widget.js",
            "kpi_dashboard/static/src/scss/kpi_dashboard.scss",
        ],
        "web.assets_qweb": [
            "kpi_dashboard/static/src/xml/**/*",
        ],
    },
    "demo": ["demo/demo_dashboard.xml"],
    "maintainers": ["etobella"],
}
