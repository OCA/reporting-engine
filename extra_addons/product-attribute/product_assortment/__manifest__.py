# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Product Assortment',
    'summary': """
        Adds the ability to manage products assortment""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'development_status': 'Stable/Production',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/product-attribute',
    'depends': [
        'base',
        'product',
    ],
    'data': [
        'views/product_assortment.xml',
    ],
    'installable': True,
}
