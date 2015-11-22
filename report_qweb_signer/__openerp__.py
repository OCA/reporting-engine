# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Qweb PDF reports signer",
    "summary": "Sign Qweb PDFs usign a PKCS#12 certificate",
    "version": "8.0.1.0.0",
    "category": "Reporting",
    "website": "http://www.antiun.com",
    "author": "Antiun Ingeniería S.L., "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "report",
    ],
    "external_dependencies": {
        "bin": ['/usr/bin/java'],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/report_certificate_view.xml",
        "views/res_company_view.xml",
    ],
    "demo": [
        "demo/report_partner.xml",
        "demo/report_certificate.xml",
    ],
}
