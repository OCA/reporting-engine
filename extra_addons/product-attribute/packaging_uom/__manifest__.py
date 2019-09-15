# Copyright 2015-2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Packaging UOM",
    "version": "12.0.1.0.0",
    "author": 'ACSONE SA/NV, '
              'Odoo Community Association (OCA)',
    "category": "Warehouse",
    "development_status": "Production/Stable",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/product-attribute",
    'summary': "Use uom in package",
    "depends": [
        "uom",
        "product",
    ],
    "data": [
        "views/product_packaging_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
