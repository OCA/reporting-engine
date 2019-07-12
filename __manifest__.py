# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

{
    "name": "Architecture & Construction",
    "version": "1.0",
    "description": """
        Application for Architecture & Construction
    """,
    "author": "hunghn.qna@gmail.com",
    "website": "https://vifuna.vn",
    'category': "Custom",
    "depends": [
        "base",
        'sale',
        'report_xlsx_helper'
    ],
    "data": [
        # =============== DATA ===================

        # =============== SECURITY ===============
        'security/ir.model.access.csv',
        # =============== VIEWS ==================
        'views/sale/sale_order_view.xml',
        'views/product/product_template_view.xml',
        'views/product/product_template_attribute_value_view.xml',
        # =============== WIZARDS ================

        # =============== MENU ===================

        # =============== REPORT =================

    ],
    "qweb": [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
