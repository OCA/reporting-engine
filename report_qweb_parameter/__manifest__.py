# -*- coding: utf-8 -*-
# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# noinspection PyStatementEffect
{
    "name": "Report QWeb Parameter",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "summary": """
        Add new parameters for qweb templates in order to reduce field length
        and check minimal length
    """,
    "author": "Creu Blanca,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/oca/reporting-engine",
    "category": "Technical Settings",
    "depends": [
        "report",
    ],
    "data": [
    ],
    "demo": [
        "demo/test_report_field_length.xml"
    ],
    "installable": True,
}
