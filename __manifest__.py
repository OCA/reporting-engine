# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

{
    "name": "Architecture & Construction Project",
    "version": "1.0",
    "description": """
        Application for Architecture & Construction
    """,
    "author": "hunghn.erp@gmail.com",
    "website": "https://vifuna.vn",
    'category': "Custom",
    "depends": [

        # Native Odoo
        "base",
        'project',
        'project_timesheet_holidays',

        # Customize Module
        'arch_construction'

    ],
    "data": [
        # Security
        'security/ir.model.access.csv',
        # =============== DATA ===================
        'data/project_group_data.xml',
        'data/project_stage_data.xml',
        # =============== SECURITY ===============

        # =============== VIEWS ==================
        'views/project/project_project_view.xml',
        'views/project/project_task_type_view.xml',
        'views/project/project_stage_view.xml',
        'views/project/project_task_view.xml',
        'views/sale/sale_order_view.xml',
        # =============== WIZARDS ================

        # =============== MENU ===================
        'menu/menu.xml',
        # =============== REPORT =================

    ],
    "qweb": [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
