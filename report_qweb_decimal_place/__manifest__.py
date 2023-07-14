# Copyright 2022 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
{
    "name": "Report Qweb Decimal Place",
    "category": "Reporting",
    "version": "16.0.1.0.0",
    "author": "Quartile Limited, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "reports/price_unit_value_format.xml",
        "views/res_currency_views.xml",
    ],
    "installable": True,
}
