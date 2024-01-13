# Copyright 2024 Quartile Limited (https://www.quartile.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Report QWeb Decimal Precision",
    "version": "16.0.1.0.0",
    "category": "Technical Settings",
    "license": "AGPL-3",
    "author": "Quartile Limited, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["uom"],
    "data": [
        "security/ir.model.access.csv",
        "security/decimal_precision_qweb_security.xml",
        "views/decimal_precision_qweb_views.xml",
    ],
    "installable": True,
}
