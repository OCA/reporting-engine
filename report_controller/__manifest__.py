# Copyright 2018 Hugo Rodrigues
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Report Controller",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "summany": """
        Reimplement controller type controllers, missing since Odoo 11.0
    """,
    "author": "Hugo Rodrigues, Odoo Community Association (OCA)",
    "website": "https://github.com/oca/reporting-engine",
    "category": "Technical Settings",
    "depends": ["web"],
    "data": [
        "views/assets.xml",
        "views/ir_actions_report_view.xml"
        ]
}
