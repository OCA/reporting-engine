# -*- encoding: utf-8 -*-
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>

{
    "name": "Qweb XML Reports",
    "version": "1.0",
    "category": "Reporting",
    "author": "Odoo Community Association (OCA), Grupo ESOC",
    "license": "AGPL-3",
    "website": "https://odoo-community.org/",
    "installable": True,
    "application": False,
    "summary": "Allow to generate XML reports",
    "depends": [
        "report",
    ],
    "data": [
        "views/report_xml_templates.xml",
    ]
}
