# Copyright 2024-2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Report Qweb Field Option",
    "version": "16.0.1.0.0",
    "category": "Technical Settings",
    "license": "AGPL-3",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["uom"],
    "external_dependencies": {
        "python": ["odoo_test_helper"],
    },
    "data": [
        "security/ir.model.access.csv",
        "security/qweb_field_options_security.xml",
        "views/qweb_field_options_views.xml",
    ],
    "installable": True,
}
