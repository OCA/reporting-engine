# Copyright 2020 Creu Blanca
# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Report Qweb Encrypt",
    "summary": "Allow to encrypt qweb pdfs",
    "version": "14.0.1.1.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Ecosoft,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": [
        "web",
    ],
    "data": ["views/ir_actions_report.xml", "templates/assets.xml"],
    "installable": True,
    "maintainers": ["kittiu"],
}
