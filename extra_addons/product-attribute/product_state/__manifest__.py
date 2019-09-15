# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "Product State",
    'summary': """
        Module introducing a state field on product template""",
    'author': 'ACSONE SA/NV, Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/product-attribute",
    'category': 'Product',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'product',
    ],
    'data': [
        'views/product_views.xml',
    ],
    'application': True,
}
