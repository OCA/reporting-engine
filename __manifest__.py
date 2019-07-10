# -*- coding: utf-8 -*-
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
    ],
    "data": [
        # =============== DATA ===================

        # =============== SECURITY ===============

        # =============== VIEWS ==================
        'views/sale_order_view.xml',
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
