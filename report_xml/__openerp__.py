# -*- encoding: utf-8 -*-
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>

{
    "name": "Qweb XML Reports",
    "version": "8.0.1.0.0",
    "category": "Reporting",
    "website": "https://grupoesoc.es",
    "author": "Grupo ESOC Ingeniería de Servicios, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
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
