# Copyright 2012 - Now Savoir-faire Linux <https://www.savoirfairelinux.com/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Key Performance Indicator",
    "version": "16.0.1.0.0",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "license": "AGPL-3",
    "category": "Report",
    "depends": ["base_external_dbsource"],
    "data": [
        "security/kpi_security.xml",
        "security/ir.model.access.csv",
        "views/kpi_category_views.xml",
        "views/kpi_history_views.xml",
        "views/kpi_views.xml",
        "views/menu.xml",
        "data/kpi_data.xml",
    ],
    "images": [
        "images/kpi_definition.png",
        "images/kpi_computation.png",
    ],
    "installable": True,
}
