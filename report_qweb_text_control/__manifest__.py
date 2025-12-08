# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "QWeb Text Control",
    "summary": "Controls whitespace and special characters in text QWeb reports",
    "version": "14.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/OCA/reporting-engine",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
    ],
    "data": [
        "views/ir_actions_report_views.xml",
    ],
    "demo": [
        "demo/partner_report.xml",
    ],
}
