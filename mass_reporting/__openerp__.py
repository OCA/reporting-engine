# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Mass Reporting",
    "summary": "Generate a large volume of reports.",
    "version": "8.0.1.0.0",
    "category": "Tools",
    "website": "http://osiell.com/",
    "author": "ABF OSIELL, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "depends": [
        "mail",
        "connector",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "data/mail_message_subtype.xml",
        "views/menu.xml",
        "views/mass_report.xml",
        "views/mass_report_attachment.xml",
    ],
    "demo": [
        "demo/mass_report.xml",
    ],
    "external_dependencies": {
        'python': ['PyPDF2'],
    },
}
