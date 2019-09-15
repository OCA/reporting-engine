# -*- coding: utf-8 -*-
# Copyright 2016 Trobz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Vietnamese states (Provinces)",
    "summary": "Vietnamese states (Provinces)",
    "version": "12.0.1.0.0",
    "category": "localization",
    "website": "https://trobz.com",
    "author": "Trobz, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "contacts",
    ],
    "data": [
        # data
        "data/res_country_state.xml",
        "data/res_country_state_district.xml",
        "data/res_country_state_district_ward.xml",

        # view
        'views/res_country_state_district_view.xml',
        'views/res_country_state_district_ward_view.xml',

        # security
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
