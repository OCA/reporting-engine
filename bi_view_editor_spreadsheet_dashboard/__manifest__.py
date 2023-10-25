# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "BI View Editor Spreadsheet Dashboard",
    "summary": "Glue module for BI View Editor and Spreadsheet Dashboard",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Hidden",
    "version": "16.0.1.0.0",
    "depends": [
        "bi_view_editor",
        "spreadsheet_dashboard",
    ],
    "data": [
        "views/menus.xml",
    ],
    "auto_install": True,
}
