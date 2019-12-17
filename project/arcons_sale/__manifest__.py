# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

{
    "name": "Architecture & Construction for Sale",
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
        'sale_management',
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
        'views/product/product_attribute_view.xml',
        # =============== WIZARDS ================
        'wizards/product/attr_value_modify_wizard.xml',
        # =============== MENU ===================

        # =============== REPORT =================
        'reports/sale_report.xml',

    ],
    "qweb": [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
