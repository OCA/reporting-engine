# Copyright 2023 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Shared Custom View",
    "version": "15.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "category": "Productivity",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["board"],
    "data": ["security/shared_custom_view_security.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
    "development_status": "Alpha",
    "maintainers": ["gurneyalex"],
}
