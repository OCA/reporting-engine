# -*- coding: utf-8 -*-
# Copyright 2015 bloopark systems (<http://bloopark.de>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Report Barcode Elaphe",
    'summary': "Barcode generation controller using elaphe library.",
    'author': "bloopark systems GmbH & Co. KG",
    'website': "http://www.bloopark.de",
    'license': 'AGPL-3',
    'category': 'Base',
    'version': '8.0.1.0.0',

    'depends': [
        'report',
        'web'
    ],
    "external_dependencies": {
        'python': ['elaphe']
    },

}
