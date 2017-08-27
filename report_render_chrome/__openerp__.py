# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Chrome reports",
    "version": "9.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Base",
    "summary": "Render reports using Chrome headless mode",
    "depends": [
        "report",
    ],
    "demo": [
        "demo/templates.xml",
        "demo/ir_actions_report_xml.xml",
    ],
    "data": [
        "views/layouts.xml",
        "views/ir_actions.xml",
    ],
    "external_dependencies": {
        'python': ['websocket'],
    },
}
